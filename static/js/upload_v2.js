
//====================================
// BAYAN OCR - Upload
//====================================

const fileInput = document.getElementById("fileInput");
const previewImage = document.getElementById("previewImage");
const pdfPreview = document.getElementById("pdfPreview");
const dropArea = document.getElementById("dropArea");
const fileName = document.getElementById("fileName");

const uploadPlaceholder =
    document.getElementById("uploadPlaceholder");

const selectedFilePreview =
    document.getElementById("selectedFilePreview");

const progress = document.getElementById("progress");
const statusText = document.getElementById("status");
const resultBox = document.getElementById("result");

const extractBtn = document.getElementById("extractBtn");

let selectedFile = null;


//====================================
// اختيار ملف
//====================================

if (fileInput) {
    fileInput.addEventListener("change", function () {
        if (this.files.length === 0) return;

        selectedFile = this.files[0];
        previewFile(selectedFile);
    });
}


//====================================
// معاينة الملف
//====================================

function previewFile(file) {

    if (!file) return;

    if (fileName) {
        fileName.textContent = file.name;
    }

    if (uploadPlaceholder) {
        uploadPlaceholder.style.display = "none";
    }

    if (selectedFilePreview) {
        selectedFilePreview.style.display = "flex";
    }

    if (file.type.startsWith("image")) {

        const reader = new FileReader();

        reader.onload = function (e) {

            if (previewImage) {
                previewImage.src = e.target.result;
                previewImage.style.display = "block";
            }

            if (pdfPreview) {
                pdfPreview.style.display = "none";
            }

        };

        reader.readAsDataURL(file);

    }

    else if (
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf")
    ) {

        if (previewImage) {
            previewImage.src = "";
            previewImage.style.display = "none";
        }

        if (pdfPreview) {
            pdfPreview.style.display = "flex";
        }

    }

    if (statusText) {
        statusText.innerHTML = "✅ تم اختيار الملف بنجاح";
    }

    if (progress) {
        progress.style.width = "10%";
    }

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

        if (e.dataTransfer.files.length === 0) return;

        selectedFile = e.dataTransfer.files[0];
        previewFile(selectedFile);
    });
}


//====================================
// EXTRACT DATA
//====================================

if (extractBtn) {
    extractBtn.addEventListener("click", async (event) => {

        event.preventDefault();

        if (!selectedFile) {
            alert("الرجاء اختيار صورة أو ملف PDF أولاً.");
            return;
        }

        const formData = new FormData();
        formData.append("image", selectedFile);

        statusText.innerHTML = "🔍 جاري قراءة النموذج...";
        progress.style.width = "20%";

        let value = 20;

        const loading = setInterval(() => {
            if (value < 90) {
                value += 5;
                progress.style.width = value + "%";
            }
        }, 200);

        try {
            const response = await fetch("/upload-image", {
                method: "POST",
                body: formData
            });

            clearInterval(loading);

            const result = await response.json();

            if (response.ok && result.success) {

                progress.style.width = "100%";

                statusText.innerHTML =
                    "✅ تم استخراج البيانات بنجاح، جاري الانتقال للمراجعة...";


                sessionStorage.setItem(
                    "bayanExtractedData",
                    JSON.stringify(result.data)
                );


                setTimeout(() => {

                    window.location.href = "/result?image=" + encodeURIComponent(result.image);

                }, 500);

            } else {

                statusText.innerHTML = "❌ تعذر استخراج البيانات";
                alert(result.message || "حدث خطأ أثناء استخراج البيانات.");

            }

        } catch (error) {

            clearInterval(loading);
            progress.style.width = "0%";

            statusText.innerHTML = "❌ تعذر الاتصال بالخادم";
            console.log(error);
        }
    });
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
// RESET
//====================================

function resetUpload() {

    selectedFile = null;

    if (fileInput) fileInput.value = "";

    progress.style.width = "0%";
    statusText.innerHTML = "بانتظار اختيار صورة أو ملف PDF...";

    if (fileName) fileName.innerHTML = "لم يتم اختيار أي صورة أو ملف PDF";

    if (previewImage) {
        previewImage.src = "";
        previewImage.style.display = "none";
    }

    if (pdfPreview) {
        pdfPreview.style.display = "none";
    }

    if (uploadPlaceholder) {
        uploadPlaceholder.style.display = "block";
    }

    if (selectedFilePreview) {
        selectedFilePreview.style.display = "none";
    }

    if (resultBox) {
        resultBox.innerHTML = `
            <p>
                بعد الضغط على <strong>"استخراج البيانات"</strong>
                ستظهر البيانات المستخرجة هنا، ويمكنك مراجعتها قبل الحفظ.
            </p>
        `;
    }
}


//====================================
// END
//====================================

console.log("✅ Bayan OCR Upload Loaded Successfully");