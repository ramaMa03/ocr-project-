
//==================================
// BAYAN OCR DASHBOARD
//==================================


//==============================
// DARK MODE
//==============================

const darkBtn = document.getElementById("dark");
const logo = document.getElementById("logo");

function setTheme(theme){

    if(theme==="dark"){

        document.body.classList.add("dark");

        if(darkBtn){
            darkBtn.innerHTML='<i class="fa-solid fa-sun"></i>';
        }

        if(logo){
            logo.src="/static/images/logo-dark.jpg";
        }

    }else{

        document.body.classList.remove("dark");

        if(darkBtn){
            darkBtn.innerHTML='<i class="fa-solid fa-moon"></i>';
        }

        if(logo){
            logo.src="/static/images/logo.jpg";
        }

    }

    localStorage.setItem("theme",theme);

}

const savedTheme=localStorage.getItem("theme");

if(savedTheme){

    setTheme(savedTheme);

}else{

    setTheme("light");

}

if(darkBtn){

darkBtn.addEventListener("click",()=>{

    if(document.body.classList.contains("dark")){

        setTheme("light");

    }else{

        setTheme("dark");

    }

});

}


//==============================
// CHART
//==============================

const ctx=document.getElementById("myChart");

if(ctx){

new Chart(ctx,{

type:"bar",

data:{

labels:["الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس"],

datasets:[{

label:"عدد العمليات",

data:[0,0,0,0,0],

borderWidth:2,

borderRadius:8

}]

},

options:{

responsive:true,

plugins:{

legend:{

display:false

}

},

scales:{

y:{

beginAtZero:true

}

}

}

});

}


//==============================
// GREETING
//==============================

const title=document.querySelector(".topbar h1");

if(title){

const hour=new Date().getHours();

if(hour<12){

title.innerHTML="☀️ صباح الخير";

}else if(hour<18){

title.innerHTML="🌤️ مساء الخير";

}else{

title.innerHTML="🌙 أهلاً بك";

}

}


//==============================
// LIVE CLOCK
//==============================

const icons=document.querySelector(".icons");

if(icons){

const clock=document.createElement("div");

clock.id="clock";

icons.prepend(clock);

function updateClock(){

clock.innerHTML=new Date().toLocaleTimeString("ar-SA");

}

updateClock();

setInterval(updateClock,1000);

}


//==============================
// CARD EFFECT
//==============================

document.querySelectorAll(".card").forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.style.transform="translateY(-8px)";

});

card.addEventListener("mouseleave",()=>{

card.style.transform="translateY(0)";

});

});
/* ====================================
        MOBILE SIDEBAR MENU
==================================== */

document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.querySelector(".sidebar");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    if (!menuToggle || !sidebar || !sidebarOverlay) {
        return;
    }

    function openMenu() {

        sidebar.classList.add("open");
        sidebarOverlay.classList.add("active");
        document.body.classList.add("menu-open");

        menuToggle.setAttribute("aria-expanded", "true");

        menuToggle.innerHTML =
            '<i class="fa-solid fa-xmark"></i>';
    }


    function closeMenu() {

        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("active");
        document.body.classList.remove("menu-open");

        menuToggle.setAttribute("aria-expanded", "false");

        menuToggle.innerHTML =
            '<i class="fa-solid fa-bars"></i>';
    }


    menuToggle.addEventListener("click", function () {

        if (sidebar.classList.contains("open")) {

            closeMenu();

        } else {

            openMenu();

        }

    });


    sidebarOverlay.addEventListener("click", function () {

        closeMenu();

    });


    /* إغلاق القائمة عند الضغط على أي رابط */
    sidebar.querySelectorAll("a").forEach(function (link) {

        link.addEventListener("click", function () {

            closeMenu();

        });

    });


    /* عند الرجوع للشاشة الكبيرة */
    window.addEventListener("resize", function () {

        if (window.innerWidth > 576) {

            closeMenu();

        }

    });

});