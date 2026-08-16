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

# OCR reader improved: preprocessing + EasyOCR (primary) + Tesseract (fallback/ensemble)
# Supports reading from image file paths or from camera (numpy frames).
# Usage:
# - From file: text = extract_text("/path/to/image.jpg")
# - From camera: capture_and_ocr()

# ---------- Preprocessing helpers ----------

def _read_image(path_or_array):
    # If given a numpy array (frame), return it directly
    if isinstance(path_or_array, np.ndarray):
        return path_or_array

    path = path_or_array
    # Handles unicode paths on Windows by reading raw bytes first
    arr = None
    try:
        arr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        arr = cv2.imread(path)
    if arr is None:
        raise FileNotFoundError(f"Could not open image: {path}")
    return arr


def _to_grayscale(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def _deskew(gray):
    # compute the angle of rotation and rotate to correct skew
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


def preprocess_image(path_or_array, scale_up=True):
    img = _read_image(path_or_array)
    gray = _to_grayscale(img)

    # denoise while preserving edges
    den = cv2.bilateralFilter(gray, 9, 75, 75)

    # optionally deskew before threshold
    den = _deskew(den)

    # adaptive threshold to handle lighting variations
    th = cv2.adaptiveThreshold(den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 15, 9)

    # morphological opening to remove small noise
    kernel = np.ones((1, 1), np.uint8)
    morph = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    # scale up small images to improve OCR accuracy
    h, w = morph.shape[:2]
    if scale_up and max(h, w) < 1200:
        scale = max(1.0, 1200.0 / max(h, w))
        morph = cv2.resize(morph, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

    return morph


# ---------- OCR backends ----------

_easy_reader = None

def ocr_easyocr(image):
    global _easy_reader
    if _easy_reader is None:
        # lazy load reader; set gpu=True if your machine has CUDA
        _easy_reader = easyocr.Reader(['ar', 'en'], gpu=False)

    # EasyOCR accepts numpy arrays; we pass the preprocessed image
    results = _easy_reader.readtext(image, detail=1)
    words = []
    for bbox, text, conf in results:
        txt = str(text).strip()
        if txt == "":
            continue
        words.append({'text': txt, 'conf': float(conf)})
    return words


def ocr_tesseract(image):
    # pytesseract expects color/BGR or PIL; convert grayscale to BGR
    if len(image.shape) == 2:
        bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        bgr = image

    config = r'--oem 3 --psm 6'  # OEM 3 = LSTM, PSM 6 = block of text
    try:
        data = pytesseract.image_to_data(bgr, lang='ara+eng', config=config, output_type=pytesseract.Output.DATAFRAME)
    except Exception:
        # fallback to simple string output
        txt = pytesseract.image_to_string(bgr, lang='ara+eng', config=config)
        txt = txt.strip()
        return [{'text': txt, 'conf': 50.0}] if txt else []

    words = []
    if data is None or data.empty:
        return words
    for _, row in data.iterrows():
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


# Optional: OCR.space remote fallback (if user prefers cloud)

def ocr_space_api_from_path(image_path, api_key, language='ara+eng'):
    url = 'https://api.ocr.space/parse/image'
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'apikey': api_key, 'language': language, 'isOverlayRequired': False}
        r = requests.post(url, files=files, data=data, timeout=60)
    res = r.json()
    if res.get('IsErroredOnProcessing'):
        raise RuntimeError('OCR.space error: ' + str(res.get('ErrorMessage')))
    parsed = res.get('ParsedResults', [])
    if not parsed:
        return ''
    return parsed[0].get('ParsedText', '')


# ---------- Postprocessing ----------

def _remove_diacritics_ar(text):
    arabic_diacritics = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
    return re.sub(arabic_diacritics, '', text)


def _normalize_spaces(text):
    return re.sub(r"\s+", ' ', text).strip()


def _reshape_bidi_arabic(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# ---------- Merge results (simple heuristic) ----------

def _choose_by_confidence(list1, list2):
    # Build average confidences and pick better list or merge token-by-token
    def avg_conf(lst):
        if not lst:
            return 0.0
        return sum(w.get('conf', 0.0) for w in lst) / len(lst)

    a1 = avg_conf(list1)
    a2 = avg_conf(list2)

    if a1 > a2 + 5:
        return list1
    if a2 > a1 + 5:
        return list2

    # confidences close: combine by position (prefer higher-confidence token)
    merged = []
    n = max(len(list1), len(list2))
    for i in range(n):
        w1 = list1[i] if i < len(list1) else None
        w2 = list2[i] if i < len(list2) else None
        if w1 and w2:
            merged.append(w1 if w1['conf'] >= w2['conf'] else w2)
        else:
            merged.append(w1 or w2)
    return merged


# ---------- Public function ----------

def extract_text(image_input, use_ocr_space=False, ocr_space_api_key=None, return_words=False):
    """
    Extracts text from an image (file path or numpy array) using a local ensemble of EasyOCR and Tesseract.

    Parameters:
    - image_input: path to the image file or numpy array (frame)
    - use_ocr_space: if True, will call OCR.space API as an additional fallback (requires api key)
    - ocr_space_api_key: your OCR.space API key
    - return_words: if True returns (final_text, words_list) else returns final_text

    Returns:
    - final text string (or tuple if return_words=True)
    """
    img = preprocess_image(image_input)

    easy = ocr_easyocr(img)
    tesser = ocr_tesseract(img)

    # prefer EasyOCR if clearly better, else merge
    merged = _choose_by_confidence(easy, tesser)

    texts = [w['text'] for w in merged]
    final = ' '.join(texts)

    # if very short or empty, try OCR.space as fallback (if requested and input is path)
    if (not final or len(final.strip()) < 3) and use_ocr_space and ocr_space_api_key and isinstance(image_input, str):
        try:
            final = ocr_space_api_from_path(image_input, ocr_space_api_key, language='ara+eng')
        except Exception:
            pass

    # postprocess
    final = _remove_diacritics_ar(final)
    final = _normalize_spaces(final)

    if return_words:
        return final, merged
    return final


# ---------- Camera capture helper ----------

def capture_and_ocr(camera_index=0, use_ocr_space=False, ocr_space_api_key=None, show_preview=True):
    """
    Opens the camera, shows a live preview. Press 'c' to capture and OCR the current frame.
    Press 'q' to quit.

    Returns the last OCR text extracted or None if none.
    """
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
                # capture and run OCR
                print('Captured frame - running OCR...')
                try:
                    text = extract_text(frame, use_ocr_space=use_ocr_space, ocr_space_api_key=ocr_space_api_key)
                    print('--- OCR RESULT ---')
                    print(text)
                    last_text = text
                except Exception as e:
                    print('OCR error:', e)
            elif key == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return last_text


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python ocr_reader.py <image> OR python ocr_reader.py --camera')
        sys.exit(1)

    if sys.argv[1] in ('--camera', 'camera'):
        # optional: pass camera index as second argument
        cam_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        capture_and_ocr(camera_index=cam_idx)
        sys.exit(0)

    path = sys.argv[1]
    # if path is a file, run OCR on it
    text, words = extract_text(path, return_words=True)
    print('----- OCR TEXT -----')
    print(text)
    print('\n----- TOKENS -----')
    for w in words:
        print(f"{w['conf']:.1f}\t{w['text']}")
