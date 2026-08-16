
//==============================
// BAYAN OCR CAMERA
//==============================

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("capture");
const startBtn = document.getElementById("startCamera");
const preview = document.getElementById("preview");
const uploadInput = document.getElementById("imageInput");

let stream = null;

//==============================
// تشغيل الكاميرا
//==============================

async function startCamera() {

    try {

        stream = await navigator.mediaDevices.getUserMedia({

            video: {
                facingMode: "environment"
            },

            audio: false

        });

        video.srcObject = stream;

        video.play();

    } catch (error) {

        alert("تعذر تشغيل الكاميرا.");

        console.error(error);

    }

}

//==============================
// التقاط الصورة
//==============================

function captureImage() {

    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(

        video,
        0,
        0,
        canvas.width,
        canvas.height

    );

    const image = canvas.toDataURL("image/jpg");

    preview.src = image;

    preview.style.display = "block";

}

//==============================
// إيقاف الكاميرا
//==============================

function stopCamera() {

    if (stream) {

        stream.getTracks().forEach(track => {

            track.stop();

        });

    }

}

//==============================
// رفع صورة من الجهاز
//==============================

uploadInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {

        preview.src = e.target.result;

        preview.style.display = "block";

    }

    reader.readAsDataURL(file);

});

//==============================
// الأزرار
//==============================

startBtn.addEventListener("click", startCamera);

captureBtn.addEventListener("click", captureImage);

//==============================
// عند إغلاق الصفحة
//==============================

window.addEventListener("beforeunload", () => {

    stopCamera();

});