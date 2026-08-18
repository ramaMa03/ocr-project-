
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
    const reader = new FileReader();

    if (fileName) {
        fileName.innerHTML = "📄 " + file.name;
    }

    if (file.type.startsWith("image")) {
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            previewImage.style.display = "block";
            previewPDF.style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    else if (file.type === "application/pdf") {
        reader.onload = function (e) {
            previewPDF.src = e.target.result;
            previewPDF.style.display = "block";
            previewImage.style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    statusText.innerHTML = "✅ تم اختيار الملف بنجاح";
    progress.style.width = "10%";
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
                statusText.innerHTML = "✅ تم استخراج البيانات بنجاح";

                displayExtractedData(result.data);

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
// عرض البيانات المستخرجة
//====================================

function displayExtractedData(data) {

    if (!resultBox) return;

    resultBox.innerHTML = `
        <div class="extracted-fields">

            <div class="field">
                <label>اسم المواطن</label>
                <input type="text" id="client_name" value="${escapeHtml(data.client_name || "")}">
            </div>

            <div class="field">
                <label>رقم الخطاب</label>
                <input type="text" id="letter_number" value="${escapeHtml(data.letter_number || "")}">
            </div>

            <div class="field">
                <label>التاريخ</label>
                <input type="text" id="date" value="${escapeHtml(data.date || "")}">
            </div>

            <div class="field">
                <label>الجهة</label>
                <input type="text" id="organization" value="${escapeHtml(data.organization || "")}">
            </div>

            <button type="button" id="saveBtn" class="save-btn">
                <i class="fa-solid fa-floppy-disk"></i>
                حفظ البيانات
            </button>

        </div>
    `;

    const saveBtn = document.getElementById("saveBtn");

    if (saveBtn) {
        saveBtn.addEventListener("click", saveData);
    }
}


//====================================
// حفظ البيانات
//====================================

async function saveData() {

    const data = {
        client_name: document.getElementById("client_name").value.trim(),
        letter_number: document.getElementById("letter_number").value.trim(),
        date: document.getElementById("date").value.trim(),
        organization: document.getElementById("organization").value.trim()
    };

    try {
        const response = await fetch("/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {

            alert("✅ تم حفظ البيانات وأرشفتها بنجاح.");
            window.location.href = "/result?id=" + result.id;

        } else {
            alert(result.message || "حدث خطأ أثناء الحفظ.");
        }

    } catch (error) {
        console.log(error);
        alert("تعذر الاتصال بالخادم.");
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

    if (previewPDF) {
        previewPDF.src = "";
        previewPDF.style.display = "none";
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
