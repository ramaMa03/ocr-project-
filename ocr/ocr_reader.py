import cv2
import numpy as np
import easyocr
import pytesseract
import requests
import arabic_reshaper
from bidi.algorithm import get_display
import re
import tempfile
import os
from collections import Counter, defaultdict

# Robust OCR reader with multiple preprocessing variants + ensemble voting.
# Reads from image path or numpy frame. Saves captures if SAVE_CAPTURES env var set.
# Usage: extract_text(path_or_frame, prefer_engine='ensemble', return_words=True)

# ---------- Configurable parameters ----------
EASYOCR_LANGS = ['ar', 'en']
EASYOCR_GPU = False  # set True if you have CUDA and torch installed
TESSER_LANG = 'ara+eng'
TESSER_PSM = '6'  # default page segmentation mode
SAVE_CAPTURES_DIR = os.environ.get('SAVE_CAPTURES', 'captures')
os.makedirs(SAVE_CAPTURES_DIR, exist_ok=True)

# ---------- Helpers ----------

def _read_image(path_or_array):
    if isinstance(path_or_array, np.ndarray):
        return path_or_array
    path = path_or_array
    arr = None
    try:
        arr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        arr = cv2.imread(path)
    if arr is None:
        raise FileNotFoundError(f"Could not open image: {path}")
    return arr


def _to_bgr(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def _to_grayscale(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def _increase_contrast(gray, alpha=1.3, beta=10):
    return cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)


def _denoise(gray):
    return cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)


def _sharpen(gray):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(gray, -1, kernel)


def _threshold_otsu(gray):
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def _adaptive_thresh(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 15, 9)


def _deskew(gray):
    coords = np.column_stack(np.where(gray < 255))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def _resize_for_ocr(img, target_max=1600):
    h, w = img.shape[:2]
    m = max(h, w)
    if m > target_max:
        scale = target_max / m
        return cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    if m < 800:
        scale = 1200.0 / max(1, m)
        return cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)
    return img


# ---------- Preprocessing variants generator ----------

def generate_variants(img):
    """Return list of grayscale image variants for OCR."""
    variants = []
    img = _resize_for_ocr(img)
    gray = _to_grayscale(img)

    # base: deskew + adaptive thresh
    g1 = _deskew(gray)
    variants.append(_adaptive_thresh(g1))

    # contrast boosted + denoise + otsu
    g2 = _increase_contrast(gray, alpha=1.4, beta=12)
    g2 = _denoise(g2)
    g2 = _deskew(g2)
    variants.append(_threshold_otsu(g2))

    # sharpened + adaptive
    g3 = _sharpen(gray)
    g3 = _deskew(g3)
    variants.append(_adaptive_thresh(g3))

    # denoised only (may preserve faint lines)
    g4 = _denoise(gray)
    g4 = _deskew(g4)
    variants.append(_adaptive_thresh(g4))

    # simple blurred then otsu (for low-contrast)
    g5 = cv2.GaussianBlur(gray, (3, 3), 0)
    g5 = _deskew(g5)
    variants.append(_threshold_otsu(g5))

    # return unique by bytes
    uniq = []
    seen = set()
    for v in variants:
        key = v.tobytes()[:64]
        if key not in seen:
            seen.add(key)
            uniq.append(v)
    return uniq


# ---------- OCR backends ----------
_easy_reader = None

def _init_easyocr():
    global _easy_reader
    if _easy_reader is None:
        _easy_reader = easyocr.Reader(EASYOCR_LANGS, gpu=EASYOCR_GPU)
    return _easy_reader


def run_easyocr_on(gray):
    reader = _init_easyocr()
    # EasyOCR expects color or gray; pass gray
    results = reader.readtext(gray, detail=1)
    words = []
    for bbox, text, conf in results:
        txt = str(text).strip()
        if not txt:
            continue
        words.append({'text': txt, 'conf': float(conf)})
    return words


def run_tesseract_on(gray):
    # convert to BGR for pytesseract
    bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) if len(gray.shape) == 2 else gray
    config = f'--oem 3 --psm {TESSER_PSM}'
    try:
        df = pytesseract.image_to_data(bgr, lang=TESSER_LANG, config=config, output_type=pytesseract.Output.DATAFRAME)
    except Exception:
        text = pytesseract.image_to_string(bgr, lang=TESSER_LANG, config=config)
        text = text.strip()
        return [{'text': text, 'conf': 50.0}] if text else []
    words = []
    if df is None or df.empty:
        return words
    for _, row in df.iterrows():
        txt = str(row.get('text', '')).strip()
        if not txt or txt.lower() == 'nan':
            continue
        conf = row.get('conf', 0)
        try:
            conf = float(conf)
        except Exception:
            conf = 0.0
        words.append({'text': txt, 'conf': conf})
    return words


# ---------- Postprocessing / normalization ----------

def normalize_arabic_text(text):
    text = str(text)
    # remove diacritics
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]', '', text)
    # unify alef/hamed/y
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ى', 'ي')
    # remove strange control chars and multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fix_common_ocr_errors(token):
    t = token
    # common misreads: 0/O, 1/I/l, l/١ etc — try conservative replacements
    t = t.replace('‎', '')  # remove RTL marks
    # normalize Arabic numerals to western digits if present mixed
    t = t.replace('٠', '0').replace('١', '1').replace('٢', '2').replace('٣', '3').replace('٤', '4')
    t = t.replace('٥', '5').replace('٦', '6').replace('٧', '7').replace('٨', '8').replace('٩', '9')
    # trim punctuation
    t = t.strip(' _-:.,|')
    return t


# ---------- Ensemble / voting ----------

def ensemble_text_from_runs(runs):
    """runs: list of string outputs. Return best candidate using frequency and length heuristics."""
    if not runs:
        return ''
    # normalize each run
    norm = [normalize_arabic_text(r) for r in runs]
    # prefer longest non-empty unique
    counts = Counter(norm)
    # choose by combination of frequency * length
    scored = [(c * len(s), s, counts[s]) for s, c in zip(norm, [1]*len(norm))]
    # fallback: pick longest
    best = max(norm, key=lambda s: (counts[s], len(s)))
    return best


def merge_word_runs(word_runs):
    """word_runs: list of lists of {'text','conf'} from different variants/engines
       returns merged list of tokens with best selected text and avg confidence
    """
    # flatten to sequences of tokens (split on spaces) and count occurrences per token position
    token_counters = defaultdict(Counter)
    token_conf_sums = defaultdict(float)
    token_conf_counts = defaultdict(int)

    max_len = 0
    for wr in word_runs:
        toks = [fix_common_ocr_errors(w['text']) for w in wr]
        max_len = max(max_len, len(toks))
        for i, tok in enumerate(toks):
            token_counters[i][tok] += 1
            token_conf_sums[(i, tok)] += w.get('conf', 0.0)
            token_conf_counts[(i, tok)] += 1

    merged = []
    for i in range(max_len):
        if token_counters[i]:
            # choose most common token; break ties by avg confidence
            candidates = token_counters[i].most_common()
            best_tok = None
            best_score = -1
            for tok, freq in candidates:
                avg_conf = token_conf_sums.get((i, tok), 0.0) / max(1, token_conf_counts.get((i, tok), 1))
                score = freq * (1 + avg_conf / 100.0)
                if score > best_score:
                    best_score = score
                    best_tok = tok
            avg_conf_final = token_conf_sums.get((i, best_tok), 0.0) / max(1, token_conf_counts.get((i, best_tok), 1))
            merged.append({'text': best_tok, 'conf': avg_conf_final})
    return merged


# ---------- Public function ----------

def extract_text(image_input, prefer_engine='ensemble', use_ocr_space=False, ocr_space_api_key=None, return_words=False):
    """Main entry. prefer_engine: 'tesseract','easyocr','ensemble'."""
    img = _read_image(image_input)

    # save capture optionally for debugging
    try:
        if isinstance(image_input, np.ndarray):
            tmpname = os.path.join(SAVE_CAPTURES_DIR, f'capture_{np.random.randint(1e9)}.jpg')
            cv2.imwrite(tmpname, img)
        else:
            tmpname = image_input
    except Exception:
        tmpname = None

    variants = generate_variants(img)
    all_runs_text = []
    all_word_runs = []

    # choose engine order for speed: prefer single engine when requested
    engines = []
    if prefer_engine == 'tesseract':
        engines = ['tesseract']
    elif prefer_engine == 'easyocr':
        engines = ['easyocr']
    else:
        engines = ['tesseract', 'easyocr']

    # run OCR on variants
    for v in variants:
        for engine in engines:
            try:
                if engine == 'tesseract':
                    wr = run_tesseract_on(v)
                    txt = ' '.join([fix_common_ocr_errors(w['text']) for w in wr])
                else:
                    wr = run_easyocr_on(v)
                    txt = ' '.join([fix_common_ocr_errors(w['text']) for w in wr])
                if txt:
                    all_runs_text.append(txt)
                    all_word_runs.append(wr)
            except Exception:
                continue

    # If no results and OCR.space requested, try remote
    if not all_runs_text and use_ocr_space and ocr_space_api_key and tmpname and isinstance(tmpname, str):
        try:
            remote = ocr_space_api_from_path(tmpname, ocr_space_api_key, language=TESSER_LANG)
            remote = normalize_arabic_text(remote)
            all_runs_text.append(remote)
            all_word_runs.append([{'text': t, 'conf': 60.0} for t in remote.split()])
        except Exception:
            pass

    final_text = ''
    merged_words = []
    if all_runs_text:
        final_text = ensemble_text_from_runs(all_runs_text)
        merged_words = merge_word_runs(all_word_runs)
    # fallback: try single-run simple OCR
    else:
        # last resort: try tesseract on original
        try:
            wr = run_tesseract_on(_to_grayscale(img))
            merged_words = wr
            final_text = ' '.join([fix_common_ocr_errors(w['text']) for w in wr])
        except Exception:
            final_text = ''
            merged_words = []

    final_text = normalize_arabic_text(final_text)

    if return_words:
        return final_text, merged_words
    return final_text


# ---------- Camera helper (save captures) ----------

def capture_and_ocr(camera_index=0, prefer_engine='ensemble', save_captures=True, show_preview=True):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {camera_index}")
    last_text = None
    print("Camera opened. Press 'c' to capture, 'q' to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('Failed reading frame from camera')
                break
            display = frame.copy()
            if show_preview:
                cv2.imshow('Camera - press c to capture, q to quit', display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                print('Captured frame - running OCR...')
                if save_captures:
                    fn = os.path.join(SAVE_CAPTURES_DIR, f'cap_{np.random.randint(1e9)}.jpg')
                    cv2.imwrite(fn, frame)
                    print('Saved capture to', fn)
                    text, words = extract_text(fn, prefer_engine=prefer_engine, return_words=True)
                else:
                    text, words = extract_text(frame, prefer_engine=prefer_engine, return_words=True)
                print('--- OCR RESULT ---')
                print(text)
                last_text = text
            elif key == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return last_text


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python ocr/ocr_reader.py <image> OR python ocr/ocr_reader.py --camera')
        sys.exit(1)
    if sys.argv[1] in ('--camera', 'camera'):
        cam_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        capture_and_ocr(camera_index=cam_idx)
        sys.exit(0)
    path = sys.argv[1]
    text, words = extract_text(path, return_words=True)
    print('----- OCR TEXT -----')
    print(text)
    print('\n----- TOKENS -----')
    for w in words:
        print(f"{w.get('conf', 0):.1f}\t{w.get('text','')}")
