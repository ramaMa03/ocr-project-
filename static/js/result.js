
// ====================================
// BAYAN OCR - Result Page
// ====================================


// ====================================
// العناصر
// ====================================

const form = document.getElementById("resultForm");

const saveBtn = document.getElementById("saveData");

const darkBtn = document.getElementById("dark");

const logo = document.getElementById("logo");


// ====================================
// حفظ بيانات الأرشفة
// ====================================

if (form && saveBtn) {

    form.addEventListener("submit", async (event) => {

        event.preventDefault();


        // ==================================
        // قراءة البيانات
        // ==================================

        const data = {

            client_name:
                document.getElementById("client_name").value.trim(),

            letter_number:
                document.getElementById("letter_number").value.trim(),

            date:
                document.getElementById("date").value.trim(),

            organization:
                document.getElementById("organization").value.trim()

        };


        // ==================================
        // التحقق من البيانات
        // ==================================

        if (!data.client_name) {

            alert("الرجاء إدخال اسم المواطن/ة.");

            return;

        }


        if (!data.letter_number) {

            alert("الرجاء إدخال رقم الخطاب.");

            return;

        }


        if (!data.date) {

            alert("الرجاء إدخال التاريخ.");

            return;

        }


        if (!data.organization) {

            alert("الرجاء إدخال الجهة.");

            return;

        }


        // ==================================
        // حالة الزر أثناء الحفظ
        // ==================================

        const originalText = saveBtn.innerHTML;

        saveBtn.disabled = true;

        saveBtn.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            جاري حفظ البيانات...
        `;


        try {

            // ==================================
            // إرسال البيانات إلى Flask
            // ==================================

            const response = await fetch("/save", {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(data)

            });


            const result = await response.json();


            // ==================================
            // نجاح الحفظ
            // ==================================

            if (response.ok && result.success) {

                saveBtn.innerHTML = `
                    <i class="fa-solid fa-check"></i>
                    تم الحفظ بنجاح
                `;


                alert(
                    "تم حفظ البيانات وأرشفتها بنجاح."
                );


                // الانتقال إلى الأرشيف

                setTimeout(() => {

                    window.location.href = "/archive";

                }, 700);


            } else {

                throw new Error(
                    result.message ||
                    "تعذر حفظ البيانات."
                );

            }


        } catch (error) {

            console.error(
                "SAVE ERROR:",
                error
            );


            alert(
                error.message ||
                "حدث خطأ أثناء حفظ البيانات."
            );


            // إعادة الزر لوضعه الطبيعي

            saveBtn.disabled = false;

            saveBtn.innerHTML = originalText;

        }

    });

}


// ====================================
// DARK MODE
// ====================================

function setTheme(theme) {

    const icon =
        darkBtn
            ? darkBtn.querySelector("i")
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


    } else {

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


// ====================================
// تحميل الوضع المحفوظ
// ====================================

const savedTheme =
    localStorage.getItem("theme");


if (savedTheme) {

    setTheme(savedTheme);

} else {

    setTheme("light");

}


// ====================================
// زر الوضع الليلي
// ====================================

if (darkBtn) {

    darkBtn.addEventListener(
        "click",
        () => {

            if (
                document.body.classList.contains("dark")
            ) {

                setTheme("light");

            } else {

                setTheme("dark");

            }

        }
    );

}


// ====================================
// END
// ====================================

console.log(
    "✅ Bayan OCR Result Loaded Successfully"
);