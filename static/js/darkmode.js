
const themeToggle = document.getElementById("dark");

function setTheme(theme) {

    const logo = document.getElementById("logo");

    if (theme === "dark") {

        document.body.classList.add("dark");
        themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';

        if (logo) {
            logo.src = "/static/images/logo-dark.jpg";
        }

    } else {

        document.body.classList.remove("dark");
        themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';

        if (logo) {
            logo.src = "/static/images/logo.jpg";
        }

    }

    localStorage.setItem("theme", theme);
}

const savedTheme = localStorage.getItem("theme");

if (savedTheme) {
    setTheme(savedTheme);
} else {
    setTheme("light");
}

themeToggle.addEventListener("click", () => {

    if (document.body.classList.contains("dark")) {

        setTheme("light");

    } else {

        setTheme("dark");

    }

});