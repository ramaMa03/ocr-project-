
import os
import fitz  # PyMuPDF
import easyocr

reader = easyocr.Reader(['ar', 'en'], gpu=False)


def extract_text(file_path):

    try:

        ext = os.path.splitext(file_path)[1].lower()

        # ======================
        # إذا كان الملف PDF
        # ======================

        if ext == ".pdf":

            pdf = fitz.open(file_path)

            page = pdf.load_page(0)

            pix = page.get_pixmap(dpi=300)

            image_path = file_path.replace(".pdf", ".png")

            pix.save(image_path)

            results = reader.readtext(image_path)

        else:

            results = reader.readtext(file_path)

        text = "\n".join([r[1] for r in results])

        print("\n========== OCR TEXT ==========")
        print(text)
        print("================================\n")

        return text

    except Exception as e:

        return f"خطأ في OCR: {e}"