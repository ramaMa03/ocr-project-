import os
import base64
import requests

from dotenv import load_dotenv


# ============================================================
# تحميل API KEY
# ============================================================

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
print("API KEY START:", API_KEY[:8])

if not API_KEY:
    raise Exception(
        "MISTRAL_API_KEY غير موجود في ملف .env"
    )



OCR_URL = "https://api.mistral.ai/v1/ocr"


HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}



# ============================================================
# استخراج النص من الملفات
# ============================================================

def extract_text(file_path):


    if not os.path.exists(file_path):

        print(
            "الملف غير موجود:",
            file_path
        )

        return ""



    extension = os.path.splitext(
        file_path
    )[1].lower()



    image_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".webp"

    }



    payload = None



    try:


        # ====================================================
        # PDF
        # ====================================================

        if extension == ".pdf":


            print(
                "تحضير PDF..."
            )


            with open(
                file_path,
                "rb"
            ) as f:


                encoded = base64.b64encode(
                    f.read()
                ).decode()



            payload = {


                "model":
                "mistral-ocr-latest",



                "document": {


                    "type":
                    "document_url",



                    "document_url":

                    "data:application/pdf;base64,"
                    + encoded


                }


            }



        # ====================================================
        # IMAGE
        # ====================================================

        elif extension in image_extensions:



            print(
                "تحضير صورة..."
            )



            with open(
                file_path,
                "rb"
            ) as f:


                encoded = base64.b64encode(
                    f.read()
                ).decode()



            if extension == ".png":

                mime = "image/png"


            elif extension == ".webp":

                mime = "image/webp"


            else:

                mime = "image/jpeg"




            payload = {


                "model":

                "mistral-ocr-latest",



                "document": {


                    "type":

                    "image_url",



                    "image_url":

                    f"data:{mime};base64,{encoded}"


                }


            }



        else:


            print(
                "نوع الملف غير مدعوم:",
                extension
            )

            return ""




        print(
            "إرسال الملف إلى Mistral OCR..."
        )



        response = requests.post(

            OCR_URL,

            headers=HEADERS,

            json=payload,

            timeout=180

        )



        print(
            "STATUS:",
            response.status_code
        )



        # ====================================================
        # خطأ من API
        # ====================================================

        if not response.ok:


            print(
                "Mistral Error:"
            )


            print(
                response.text
            )


            return ""





        result = response.json()



        texts = []



        for page in result.get(
            "pages",
            []
        ):


            markdown = page.get(
                "markdown",
                ""
            )



            if markdown:

                texts.append(
                    markdown
                )



        final_text = "\n\n".join(
            texts
        )



        print(
            "TEXT LENGTH:",
            len(final_text)
        )



        return final_text




    except requests.exceptions.Timeout:


        print(
            "انتهى وقت الاتصال مع Mistral"
        )

        return ""



    except Exception as e:


        print(
            "OCR ERROR:",
            e
        )

        return ""