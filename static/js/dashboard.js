
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