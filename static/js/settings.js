
//====================================
// Bayan OCR - Settings
//====================================

const themeToggle = document.getElementById("themeToggle");

const saveBtn = document.getElementById("saveSettings");

const resetBtn = document.getElementById("resetSettings");

//====================================
// تحميل الإعدادات
//====================================
window.onload = () => {

const theme = localStorage.getItem("theme");

const logo = document.querySelector(".page-logo");

if(theme === "dark"){

    document.body.classList.add("dark");

    themeToggle.checked = true;

    if(logo){
        logo.src = "/static/images/logo-dark.jpg";
    }

}
else{

    document.body.classList.remove("dark");

    themeToggle.checked = false;

    if(logo){
        logo.src = "/static/images/logo.jpg";
    }

}

};

//====================================
// تغيير الوضع الليلي
//====================================

themeToggle.addEventListener("change",()=>{

const logo = document.querySelector(".page-logo");

if(themeToggle.checked){

    document.body.classList.add("dark");

    localStorage.setItem("theme","dark");

    if(logo){
        logo.src = "/static/images/logo-dark.jpg";
    }

}
else{

    document.body.classList.remove("dark");

    localStorage.setItem("theme","light");

    if(logo){
        logo.src = "/static/images/logo.jpg";
    }

}

});

//====================================
// حفظ الإعدادات
//====================================

saveBtn.addEventListener("click",()=>{

alert("تم حفظ الإعدادات بنجاح.");

});

//====================================
// إعادة التعيين
//====================================

resetBtn.addEventListener("click",()=>{

const ok = confirm("هل تريد إعادة الإعدادات الافتراضية؟");

if(!ok) return;

localStorage.removeItem("theme");

document.body.classList.remove("dark");

themeToggle.checked = false;

alert("تمت إعادة الإعدادات.");

});

//====================================
// END
//====================================