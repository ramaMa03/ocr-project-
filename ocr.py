import os
import base64
import requests

from dotenv import load_dotenv


# ============================================================
# تحميل API Key من ملف .env
# ============================================================

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")

if not API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY غير موجود في ملف .env"
    )


# ============================================================
# إعدادات Mistral API
# ============================================================

OCR_URL = "https://api.mistral.ai/v1/ocr"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


# ============================================================
# استخراج النص
# ============================================================

def extract_text(file_path):

    # --------------------------------------------------------
    # التأكد من وجود الملف
    # --------------------------------------------------------

    if not os.path.exists(file_path):

        print("الملف غير موجود:", file_path)

        return ""


    extension = os.path.splitext(file_path)[1].lower()


    # --------------------------------------------------------
    # أنواع الصور المدعومة
    # --------------------------------------------------------

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".avif"
    }


    print("=" * 60)
    print("بدء Mistral OCR")
    print("=" * 60)

    print("FILE:", file_path)
    print("TYPE:", extension)


    try:

        # ====================================================
        # PDF
        # ====================================================

        if extension == ".pdf":

            print("جاري رفع PDF إلى Mistral...")


            # ------------------------------------------------
            # رفع الملف إلى Files API
            # ------------------------------------------------

            with open(file_path, "rb") as pdf_file:

                files = {
                    "file": (
                        os.path.basename(file_path),
                        pdf_file,
                        "application/pdf"
                    )
                }

                data = {
                    "purpose": "ocr"
                }

                upload_response = requests.post(
                    "https://api.mistral.ai/v1/files",
                    headers={
                        "Authorization":
                        f"Bearer {API_KEY}"
                    },
                    files=files,
                    data=data,
                    timeout=120
                )


            if not upload_response.ok:

                print(
                    "فشل رفع PDF:",
                    upload_response.status_code
                )

                print(
                    upload_response.text
                )

                return ""


            uploaded_file = upload_response.json()

            file_id = uploaded_file["id"]

            print("تم رفع PDF بنجاح.")
            print("FILE ID:", file_id)


            # ------------------------------------------------
            # الحصول على Signed URL
            # ------------------------------------------------

            signed_url_response = requests.get(

                f"https://api.mistral.ai/v1/files/"
                f"{file_id}/url",

                headers={
                    "Authorization":
                    f"Bearer {API_KEY}"
                },

                params={
                    "expiry": 1
                },

                timeout=30
            )


            if not signed_url_response.ok:

                print(
                    "فشل الحصول على رابط PDF:"
                )

                print(
                    signed_url_response.text
                )

                return ""


            signed_url = signed_url_response.json()["url"]

            print("تم الحصول على رابط الملف.")


            # ------------------------------------------------
            # إرسال PDF إلى OCR
            # ------------------------------------------------

            payload = {

                "model": "mistral-ocr-latest",

                "document": {

                    "type": "document_url",

                    "document_url": signed_url
                }
            }


        # ====================================================
        # الصور
        # ====================================================

        elif extension in image_extensions:

            print(
                "جاري إرسال الصورة إلى Mistral..."
            )


            # ------------------------------------------------
            # قراءة الصورة
            # ------------------------------------------------

            with open(
                file_path,
                "rb"
            ) as image_file:

                image_bytes = image_file.read()


            # ------------------------------------------------
            # تحويل الصورة إلى Base64
            # ------------------------------------------------

            encoded_image = base64.b64encode(
                image_bytes
            ).decode("utf-8")


            # ------------------------------------------------
            # تحديد MIME Type
            # ------------------------------------------------

            if extension in {
                ".jpg",
                ".jpeg"
            }:

                mime_type = "image/jpeg"

            elif extension == ".png":

                mime_type = "image/png"

            elif extension == ".webp":

                mime_type = "image/webp"

            elif extension == ".avif":

                mime_type = "image/avif"

            else:

                mime_type = "image/jpeg"


            image_url = (
                f"data:{mime_type};base64,"
                f"{encoded_image}"
            )


            # ------------------------------------------------
            # إعداد طلب OCR
            # ------------------------------------------------

            payload = {

                "model": "mistral-ocr-latest",

                "document": {

                    "type": "image_url",

                    "image_url": image_url
                }
            }


        # ====================================================
        # نوع غير مدعوم
        # ====================================================

        else:

            print(
                "نوع الملف غير مدعوم:",
                extension
            )

            return ""


        # ====================================================
        # إرسال الطلب إلى Mistral OCR API
        # ====================================================

        print("جاري إرسال الملف إلى Mistral OCR...")

        response = requests.post(

            OCR_URL,

            headers=HEADERS,

            json=payload,

            timeout=180
        )


        # ----------------------------------------------------
        # التحقق من نجاح الطلب
        # ----------------------------------------------------

        if not response.ok:

            print("=" * 60)

            print(
                "MISTRAL OCR ERROR:"
            )

            print(
                "STATUS:",
                response.status_code
            )

            print(
                response.text
            )

            print("=" * 60)

            return ""


        # ====================================================
        # قراءة النتيجة
        # ====================================================

        result = response.json()

        all_text = []


        for page in result.get(
            "pages",
            []
        ):

            markdown = page.get(
                "markdown",
                ""
            )

            if markdown:

                all_text.append(
                    markdown
                )


        extracted_text = "\n\n".join(
            all_text
        )


        # ====================================================
        # عرض النتيجة
        # ====================================================

        print("=" * 60)

        print(
            "MISTRAL OCR RESULT"
        )

        print("=" * 60)

        print(
            extracted_text
        )

        print("=" * 60)


        return extracted_text


    except requests.exceptions.Timeout:

        print("=" * 60)

        print(
            "MISTRAL OCR ERROR:"
        )

        print(
            "انتهت مهلة الاتصال بـ Mistral."
        )

        print("=" * 60)

        return ""


    except Exception as e:

        print("=" * 60)

        print(
            "MISTRAL OCR ERROR:"
        )

        print(
            type(e).__name__,
            ":",
            e
        )

        print("=" * 60)

        return ""