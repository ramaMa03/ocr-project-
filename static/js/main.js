
/*==================================
        BAYAN OCR
===================================*/

//========================
// DARK MODE
//========================

const darkBtn = document.getElementById("dark");

function updateLogos(theme) {

    const lightLogo = "/static/images/logo.jpg";
    const darkLogo = "/static/images/logo-dark.jpg";

    const logoSource = theme === "dark"
        ? darkLogo
        : lightLogo;

    // جميع الشعارات الموجودة في الصفحة
    document.querySelectorAll(
        "#logo, .project-logo, .page-logo, .logo img"
    ).forEach(logo => {

        logo.src = logoSource;

    });

    // شعار شاشة البداية
    const splashLogo = document.querySelector(".splash-logo");

    if (splashLogo) {

        splashLogo.src = logoSource;

    }

}


// تحميل الثيم المحفوظ
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {

    document.body.classList.add("dark");

    if (darkBtn) {
        darkBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }

    updateLogos("dark");

} else {

    document.body.classList.remove("dark");

    if (darkBtn) {
        darkBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }

    updateLogos("light");

}


// تغيير الثيم عند الضغط
if (darkBtn) {

    darkBtn.addEventListener("click", () => {

        if (document.body.classList.contains("dark")) {

            document.body.classList.remove("dark");

            localStorage.setItem("theme", "light");

            darkBtn.innerHTML =
                '<i class="fa-solid fa-moon"></i>';

            updateLogos("light");

        } else {

            document.body.classList.add("dark");

            localStorage.setItem("theme", "dark");

            darkBtn.innerHTML =
                '<i class="fa-solid fa-sun"></i>';

            updateLogos("dark");

        }

    });

}

//========================
// SCROLL ANIMATION
//========================

const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {
            entry.target.classList.add("show");
        }

    });

});

document.querySelectorAll(".card,.step,.member").forEach(el => {

    el.classList.add("hidden");
    observer.observe(el);

});

//========================
// BACK TO TOP BUTTON
//========================

const topBtn = document.createElement("button");

topBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
topBtn.id = "topButton";

document.body.appendChild(topBtn);

window.addEventListener("scroll", () => {

    if (window.scrollY > 300) {

        topBtn.style.opacity = "1";
        topBtn.style.visibility = "visible";

    } else {

        topBtn.style.opacity = "0";
        topBtn.style.visibility = "hidden";

    }

});

topBtn.onclick = () => {

    window.scrollTo({

        top: 0,
        behavior: "smooth"

    });

};

//========================
// HERO IMAGE EFFECT
//========================

const hero = document.querySelector(".hero-image img");

if (hero) {

    hero.addEventListener("mousemove", () => {

        hero.style.transform = "scale(1.03)";

    });

    hero.addEventListener("mouseleave", () => {

        hero.style.transform = "scale(1)";

    });

}

//========================
// RIPPLE EFFECT
//========================

document.querySelectorAll(".btn1,.btn2").forEach(btn => {

    btn.addEventListener("click", function (e) {

        const circle = document.createElement("span");

        circle.classList.add("ripple");

        this.appendChild(circle);

        const x = e.clientX - this.offsetLeft;
        const y = e.clientY - this.offsetTop;

        circle.style.left = x + "px";
        circle.style.top = y + "px";

        setTimeout(() => {

            circle.remove();

        }, 600);

    });

});

//========================
// SPLASH SCREEN
//========================

window.addEventListener("load", () => {

    const splash = document.getElementById("splash-screen");

    if (splash) {

        setTimeout(() => {

            splash.style.opacity = "0";

            setTimeout(() => {

                splash.style.display = "none";

            }, 600);

        }, 1800);

    }

});