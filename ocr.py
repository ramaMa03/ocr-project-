
import easyocr
import os
import cv2

from pdf2image import convert_from_path


# ==================================
# إنشاء قارئ OCR
# ==================================

reader = easyocr.Reader(
    ['ar', 'en'],
    gpu=False
)


# ==================================
# تحسين الصورة قبل القراءة
# ==================================

def preprocess_image(image_path):

    try:

        image = cv2.imread(image_path)

        if image is None:

            print("تعذر فتح الصورة:", image_path)

            return image_path


        # ----------------------------------
        # تكبير الصورة
        # ----------------------------------

        height, width = image.shape[:2]

        if width < 1800:

            scale = 2

            image = cv2.resize(
                image,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )


        # ----------------------------------
        # تحسين التباين
        # ----------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        # ----------------------------------
        # إزالة التشويش الخفيف
        # ----------------------------------

        gray = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21
        )


        # ----------------------------------
        # تحسين التباين
        # ----------------------------------

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced = clahe.apply(gray)


        # ----------------------------------
        # حفظ نسخة مؤقتة
        # ----------------------------------

        temp_path = image_path + "_processed.jpg"

        cv2.imwrite(
            temp_path,
            enhanced,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                95
            ]
        )


        return temp_path


    except Exception as e:

        print(
            "IMAGE PREPROCESS ERROR:",
            e
        )

        return image_path


# ==================================
# قراءة صورة واحدة
# ==================================

def read_image(image_path):

    processed_path = None

    try:

        # ----------------------------------
        # محاولة قراءة الصورة الأصلية
        # ----------------------------------

        original_result = reader.readtext(

            image_path,

            detail=1,

            paragraph=False,

            width_ths=0.7,

            height_ths=0.7,

            text_threshold=0.25,

            low_text=0.15,

            link_threshold=0.25,

            mag_ratio=1.5
        )


        # ----------------------------------
        # ترتيب النتائج
        # ----------------------------------

        original_lines = []


        for item in original_result:

            if len(item) < 2:

                continue


            box = item[0]

            text = item[1]


            if not text:

                continue


            text = text.strip()


            if not text:

                continue


            # مركز منطقة النص

            center_y = sum(
                point[1]
                for point in box
            ) / 4


            center_x = sum(
                point[0]
                for point in box
            ) / 4


            original_lines.append({

                "text": text,

                "x": center_x,

                "y": center_y

            })


        # ----------------------------------
        # ترتيب النص من أعلى إلى أسفل
        # ----------------------------------

        original_lines.sort(
            key=lambda item: (
                round(item["y"] / 25),
                -item["x"]
            )
        )


        original_text = "\n".join(

            item["text"]

            for item in original_lines

            if item["text"]

        )


        # ==================================
        # إذا كانت القراءة جيدة
        # نستخدمها مباشرة
        # ==================================

        if len(original_text.strip()) >= 15:

            print("=" * 60)

            print("OCR RESULT")

            print("=" * 60)

            print(original_text)

            print("=" * 60)

            return original_text


        # ==================================
        # إذا كانت القراءة ضعيفة
        # نحاول تحسين الصورة
        # ==================================

        print(
            "القراءة الأصلية ضعيفة، جاري تحسين الصورة..."
        )


        processed_path = preprocess_image(
            image_path
        )


        processed_result = reader.readtext(

            processed_path,

            detail=1,

            paragraph=False,

            width_ths=0.7,

            height_ths=0.7,

            text_threshold=0.25,

            low_text=0.15,

            link_threshold=0.25,

            mag_ratio=1.5
        )


        processed_lines = []


        for item in processed_result:

            if len(item) < 2:

                continue


            box = item[0]

            text = item[1]


            if not text:

                continue


            text = text.strip()


            if not text:

                continue


            center_y = sum(
                point[1]
                for point in box
            ) / 4


            center_x = sum(
                point[0]
                for point in box
            ) / 4


            processed_lines.append({

                "text": text,

                "x": center_x,

                "y": center_y

            })


        processed_lines.sort(
            key=lambda item: (
                round(item["y"] / 25),
                -item["x"]
            )
        )


        processed_text = "\n".join(

            item["text"]

            for item in processed_lines

            if item["text"]

        )


        # ==================================
        # اختيار القراءة الأفضل
        # ==================================

        if len(processed_text.strip()) > len(
            original_text.strip()
        ):

            final_text = processed_text

        else:

            final_text = original_text


        print("=" * 60)

        print("OCR RESULT")

        print("=" * 60)

        print(final_text)

        print("=" * 60)


        return final_text


    except Exception as e:

        print(
            "IMAGE OCR ERROR:",
            e
        )

        return ""


    finally:

        # ----------------------------------
        # حذف الصورة المؤقتة
        # ----------------------------------

        if processed_path:

            try:

                if os.path.exists(
                    processed_path
                ):

                    os.remove(
                        processed_path
                    )

            except Exception:

                pass


# ==================================
# استخراج النص من صورة أو PDF
# ==================================

def extract_text(file_path):

    if not os.path.exists(file_path):

        print(
            "الملف غير موجود:",
            file_path
        )

        return ""


    # ==================================
    # معرفة نوع الملف
    # ==================================

    extension = os.path.splitext(
        file_path
    )[1].lower()


    # ==================================
    # الصور المدعومة
    # ==================================

    image_extensions = [

        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff"

    ]


    # ==================================
    # قراءة الصورة
    # ==================================

    if extension in image_extensions:

        return read_image(
            file_path
        )


    # ==================================
    # PDF
    # ==================================

    if extension == ".pdf":

        try:

            print(
                "جاري تحويل صفحات PDF إلى صور..."
            )


            pages = convert_from_path(

                file_path,

                dpi=300

            )


            all_text = []


            for page_number, page in enumerate(

                pages,

                start=1

            ):

                print(
                    f"جاري قراءة الصفحة {page_number}..."
                )


                temp_image = (

                    file_path

                    + f"_page_{page_number}.jpg"

                )


                page.save(

                    temp_image,

                    "JPEG",

                    quality=95

                )


                page_text = read_image(

                    temp_image

                )


                if page_text:

                    all_text.append(

                        page_text

                    )


                # ----------------------------------
                # حذف الصورة المؤقتة
                # ----------------------------------

                try:

                    if os.path.exists(
                        temp_image
                    ):

                        os.remove(
                            temp_image
                        )

                except Exception:

                    pass


            text = "\n".join(

                all_text

            )


            print("=" * 60)

            print("PDF OCR RESULT")

            print("=" * 60)

            print(text)

            print("=" * 60)


            return text


        except Exception as e:

            print(
                "PDF OCR ERROR:",
                e
            )

            return ""


    # ==================================
    # نوع ملف غير مدعوم
    # ==================================

    print(
        "نوع الملف غير مدعوم:",
        extension
    )

    return ""