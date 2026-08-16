
//====================================
// BAYAN OCR - Upload
//====================================

const fileInput = document.getElementById("fileInput");
const previewImage = document.getElementById("previewImage");
const previewPDF = document.getElementById("previewPDF");
const dropArea = document.getElementById("dropArea");
const fileName = document.getElementById("fileName");

const progress = document.getElementById("progress");
const statusText = document.getElementById("status");
const resultBox = document.getElementById("result");

const cameraBtn = document.getElementById("cameraBtn");
const captureBtn = document.getElementById("captureBtn");
const closeCamera = document.getElementById("closeCamera");

const cameraSection = document.getElementById("cameraSection");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const extractBtn = document.getElementById("extractBtn");

let stream = null;
let selectedFile = null;


//====================================
// اختيار ملف
//====================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length === 0) {
            return;
        }

        selectedFile = this.files[0];

        previewFile(selectedFile);

    });

}


//====================================
// معاينة الملف
//====================================

function previewFile(file) {

    const reader = new FileReader();

    // عرض اسم الملف
    if (fileName) {

        fileName.innerHTML =
            "📄 " + file.name;

    }


    //================================
    // صورة
    //================================

    if (file.type.startsWith("image")) {

        reader.onload = function (e) {

            previewImage.src = e.target.result;

            previewImage.style.display = "block";

            previewPDF.style.display = "none";

        };

        reader.readAsDataURL(file);

    }


    //================================
    // PDF
    //================================

    else if (file.type === "application/pdf") {

        reader.onload = function (e) {

            previewPDF.src = e.target.result;

            previewPDF.style.display = "block";

            previewImage.style.display = "none";

        };

        reader.readAsDataURL(file);

    }


    statusText.innerHTML =
        "✅ تم اختيار الملف بنجاح";

    progress.style.width = "10%";

}


//====================================
// CAMERA
//====================================

if (cameraBtn) {

    cameraBtn.addEventListener("click", async () => {

        cameraSection.classList.add("active");

        try {

            stream =
                await navigator.mediaDevices.getUserMedia({

                    video: {
                        facingMode: "environment"
                    }

                });

            video.srcObject = stream;

        }

        catch (error) {

            alert("تعذر تشغيل الكاميرا");

            console.log(error);

        }

    });

}


//====================================
// CAPTURE IMAGE
//====================================

if (captureBtn) {

    captureBtn.addEventListener("click", () => {

        const context =
            canvas.getContext("2d");

        canvas.width =
            video.videoWidth;

        canvas.height =
            video.videoHeight;

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );


        canvas.toBlob(function (blob) {

            selectedFile = new File(
                [blob],
                "camera.jpg",
                {
                    type: "image/jpeg"
                }
            );


            previewImage.src =
                URL.createObjectURL(selectedFile);

            previewImage.style.display =
                "block";

            previewPDF.style.display =
                "none";


            // اسم الملف
            if (fileName) {

                fileName.innerHTML =
                    "📷 camera.jpg";

            }


            statusText.innerHTML =
                "📷 تم التقاط الصورة بنجاح";

            progress.style.width =
                "20%";

        }, "image/jpeg");


        if (stream) {

            stream
                .getTracks()
                .forEach(track => track.stop());

        }

        cameraSection.classList.remove("active");

    });

}


//====================================
// CLOSE CAMERA
//====================================

if (closeCamera) {

    closeCamera.addEventListener("click", () => {

        if (stream) {

            stream
                .getTracks()
                .forEach(track => track.stop());

        }

        cameraSection.classList.remove("active");

    });

}


//====================================
// DRAG & DROP
//====================================

if (dropArea) {

    dropArea.addEventListener("dragover", (e) => {

        e.preventDefault();

        dropArea.classList.add("dragover");

    });


    dropArea.addEventListener("dragleave", () => {

        dropArea.classList.remove("dragover");

    });


    dropArea.addEventListener("drop", (e) => {

        e.preventDefault();

        dropArea.classList.remove("dragover");


        if (e.dataTransfer.files.length === 0) {

            return;

        }


        selectedFile =
            e.dataTransfer.files[0];

        previewFile(selectedFile);

    });

}


//====================================
// EXTRACT DATA
//====================================

if (extractBtn) {

    extractBtn.addEventListener("click", async (event) => {

        // مهم جدًا:
        // منع إرسال الفورم بشكل طبيعي
        event.preventDefault();


        if (!selectedFile) {

            alert(
                "الرجاء اختيار صورة أو ملف PDF أولاً."
            );

            return;

        }


        const formData =
            new FormData();

        formData.append(
            "image",
            selectedFile
        );


        statusText.innerHTML =
            "🔍 جاري قراءة النموذج...";

        progress.style.width =
            "20%";


        let value = 20;


        const loading =
            setInterval(() => {

                if (value < 90) {

                    value += 5;

                    progress.style.width =
                        value + "%";

                }

            }, 200);


        try {

            const response =
                await fetch(
                    "/upload-image",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            clearInterval(loading);


            //================================
            // قراءة JSON
            //================================

            const result =
                await response.json();


            if (
                response.ok &&
                result.success
            ) {

                progress.style.width =
                    "100%";


                statusText.innerHTML =
                    "✅ تم استخراج البيانات بنجاح";


                // عرض البيانات
                displayExtractedData(
                    result.data
                );


            }

            else {

                statusText.innerHTML =
                    "❌ تعذر استخراج البيانات";


                alert(
                    result.message ||
                    "حدث خطأ أثناء استخراج البيانات."
                );

            }

        }

        catch (error) {

            clearInterval(loading);

            progress.style.width =
                "0%";


            statusText.innerHTML =
                "❌ تعذر الاتصال بالخادم";


            console.log(error);

        }

    });

}


//====================================
// عرض البيانات المستخرجة
//====================================

function displayExtractedData(data) {

    if (!resultBox) {
        return;
    }


    resultBox.innerHTML = `

        <div class="extracted-fields">

            <div class="field">

                <label>اسم المواطن</label>

                <input
                    type="text"
                    id="client_name"
                    value="${escapeHtml(data.client_name || "")}"
                >

            </div>


            <div class="field">

                <label>رقم الخطاب</label>

                <input
                    type="text"
                    id="letter_number"
                    value="${escapeHtml(data.letter_number || "")}"
                >

            </div>


            <div class="field">

                <label>التاريخ</label>

                <input
                    type="text"
                    id="date"
                    value="${escapeHtml(data.date || "")}"
                >

            </div>


            <div class="field">

                <label>الجهة</label>

                <input
                    type="text"
                    id="organization"
                    value="${escapeHtml(data.organization || "")}"
                >

            </div>


            <button
                type="button"
                id="saveBtn"
                class="save-btn"
            >

                <i class="fa-solid fa-floppy-disk"></i>

                حفظ البيانات

            </button>

        </div>

    `;


    // زر الحفظ
    const saveBtn =
        document.getElementById("saveBtn");


    if (saveBtn) {

        saveBtn.addEventListener(
            "click",
            saveData
        );

    }

}


//====================================
// حفظ البيانات
//====================================

async function saveData() {

    const data = {

        client_name:
            document.getElementById(
                "client_name"
            ).value.trim(),

        letter_number:
            document.getElementById(
                "letter_number"
            ).value.trim(),

        date:
            document.getElementById(
                "date"
            ).value.trim(),

        organization:
            document.getElementById(
                "organization"
            ).value.trim()

    };


    try {

        const response =
            await fetch(
                "/save",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(data)

                }
            );


        const result =
            await response.json();


        if (
            response.ok &&
            result.success
        ) {

            alert(
                "✅ تم حفظ البيانات وأرشفتها بنجاح."
            );


            // الانتقال لصفحة النجاح
            window.location.href =
                "/result?id=" +
                result.id;

        }

        else {

            alert(
                result.message ||
                "حدث خطأ أثناء الحفظ."
            );

        }

    }

    catch (error) {

        console.log(error);

        alert(
            "تعذر الاتصال بالخادم."
        );

    }

}


//====================================
// حماية النص من HTML
//====================================

function escapeHtml(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}


//====================================
// DARK MODE
//====================================

const dark =
    document.getElementById("dark");

const logo =
    document.getElementById("logo");


function setTheme(theme) {

    const icon =
        dark
            ? dark.querySelector("i")
            : null;


    if (theme === "dark") {

        document.body.classList.add("dark");


        if (icon) {

            icon.className =
                "fa-solid fa-sun";

        }


        if (logo) {

            logo.src =
                "/static/images/logo-dark.jpg";

        }

    }

    else {

        document.body.classList.remove("dark");


        if (icon) {

            icon.className =
                "fa-solid fa-moon";

        }


        if (logo) {

            logo.src =
                "/static/images/logo.jpg";

        }

    }


    localStorage.setItem(
        "theme",
        theme
    );

}


const savedTheme =
    localStorage.getItem("theme");


if (savedTheme) {

    setTheme(savedTheme);

}

else {

    setTheme("light");

}


if (dark) {

    dark.addEventListener(
        "click",
        () => {

            if (
                document.body.classList.contains(
                    "dark"
                )
            ) {

                setTheme("light");

            }

            else {

                setTheme("dark");

            }

        }
    );

}


//====================================
// RESET
//====================================

function resetUpload() {

    selectedFile = null;


    if (fileInput) {

        fileInput.value = "";

    }


    progress.style.width =
        "0%";


    statusText.innerHTML =
        "بانتظار اختيار صورة أو ملف PDF...";


    if (fileName) {

        fileName.innerHTML =
            "لم يتم اختيار أي صورة أو ملف PDF";

    }


    if (previewImage) {

        previewImage.src = "";

        previewImage.style.display =
            "none";

    }


    if (previewPDF) {

        previewPDF.src = "";

        previewPDF.style.display =
            "none";

    }


    if (resultBox) {

        resultBox.innerHTML = `

            <p>

                بعد الضغط على

                <strong>
                    "استخراج البيانات"
                </strong>

                ستظهر البيانات المستخرجة هنا،
                ويمكنك مراجعتها قبل الحفظ.

            </p>

        `;

    }

}


//====================================
// END
//====================================

console.log(
    "✅ Bayan OCR Upload Loaded Successfully"
);