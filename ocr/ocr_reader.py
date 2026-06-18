
import pytesseract

from PIL import Image

# مهم لو كان Tesseract في المسار الافتراضي
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text(image_path):

    try:

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image,
            lang="ara+eng"
        )

        return text

    except Exception as e:

        print("OCR Error:", e)

        return ""