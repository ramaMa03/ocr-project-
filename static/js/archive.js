
//====================================
// BAYAN OCR - Archive
//====================================


//====================================
// العناصر
//====================================

const table = document.getElementById("archiveTable");

const searchBtn = document.getElementById("searchBtn");
const resetBtn = document.getElementById("resetBtn");
const refreshBtn = document.getElementById("refreshTable");

const modal = document.getElementById("viewModal");
const modalBody = document.getElementById("modalBody");
const closeModal = document.getElementById("closeModal");

const recordCount = document.getElementById("recordCount");
const emptyMessage = document.getElementById("emptyMessage");

const darkBtn = document.getElementById("dark");
const logo = document.getElementById("logo");

let archiveData = [];


//====================================
// تحميل السجلات
//====================================

async function loadArchive() {

    try {

        const response = await fetch("/archive-data");

        if (!response.ok) {

            throw new Error("تعذر تحميل الأرشيف");

        }

        archiveData = await response.json();

        drawTable(archiveData);

    }

    catch (error) {

        console.log(error);

        table.innerHTML = "";

        if (recordCount) {

            recordCount.textContent = "0 سجل";

        }

        if (emptyMessage) {

            emptyMessage.style.display = "block";

        }

    }

}


//====================================
// رسم جدول الأرشيف
//====================================

function drawTable(data) {

    table.innerHTML = "";


    if (recordCount) {

        recordCount.textContent =
            `${data.length} سجل`;

    }


    if (!data || data.length === 0) {

        if (emptyMessage) {

            emptyMessage.style.display = "block";

        }

        return;

    }


    if (emptyMessage) {

        emptyMessage.style.display = "none";

    }


    data.forEach((record, index) => {


        const row = document.createElement("tr");


        row.innerHTML = `

            <td>
                ${index + 1}
            </td>


            <td>
                ${record.letter_number || ""}
            </td>


            <td>
                ${record.date || ""}
            </td>


            <td>
                ${record.organization || ""}
            </td>


            <td>
                ${record.client_name || ""}
            </td>


            <td>

                <button
                    class="view"
                    onclick="viewRecord(${record.id})"
                    title="عرض">

                    <i class="fa-solid fa-eye"></i>

                </button>


                <button
                    class="edit"
                    onclick="editRecord(${record.id})"
                    title="تعديل">

                    <i class="fa-solid fa-pen"></i>

                </button>


                <button
                    class="word"
                    onclick="openWord(${record.id})"
                    title="فتح Word">

                    <i class="fa-solid fa-file-word"></i>

                </button>


                <button
                    class="delete"
                    onclick="deleteRecord(${record.id})"
                    title="حذف">

                    <i class="fa-solid fa-trash"></i>

                </button>

            </td>

        `;


        table.appendChild(row);

    });

}


//====================================
// البحث
//====================================

if (searchBtn) {

    searchBtn.addEventListener("click", () => {


        const name =
            document.getElementById("searchName")
            .value
            .trim()
            .toLowerCase();


        const letter =
            document.getElementById("searchLetter")
            .value
            .trim()
            .toLowerCase();


        const date =
            document.getElementById("searchDate")
            .value;


        const department =
            document.getElementById("searchDepartment")
            .value
            .trim()
            .toLowerCase();


        const filtered = archiveData.filter(record => {


            const recordName =
                String(record.client_name || "")
                .toLowerCase();


            const recordLetter =
                String(record.letter_number || "")
                .toLowerCase();


            const recordOrganization =
                String(record.organization || "")
                .toLowerCase();


            const recordDate =
                String(record.date || "");


            return (

                recordName.includes(name) &&

                recordLetter.includes(letter) &&

                recordOrganization.includes(department) &&

                (
                    date === "" ||
                    recordDate === date
                )

            );

        });


        drawTable(filtered);

    });

}


//====================================
// إعادة تعيين البحث
//====================================

if (resetBtn) {

    resetBtn.addEventListener("click", () => {


        document.getElementById("searchName").value = "";

        document.getElementById("searchLetter").value = "";

        document.getElementById("searchDate").value = "";

        document.getElementById("searchDepartment").value = "";


        drawTable(archiveData);

    });

}


//====================================
// تحديث الجدول
//====================================

if (refreshBtn) {

    refreshBtn.addEventListener("click", () => {

        loadArchive();

    });

}


//====================================
// عرض تفاصيل السجل
//====================================

function viewRecord(id) {


    const record =
        archiveData.find(item => item.id === id);


    if (!record) {

        return;

    }


    modal.style.display = "flex";


    modalBody.innerHTML = `

        <div class="detail-row">

            <strong>اسم المواطن/ة:</strong>

            <span>
                ${record.client_name || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>رقم الخطاب:</strong>

            <span>
                ${record.letter_number || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>التاريخ:</strong>

            <span>
                ${record.date || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>الجهة:</strong>

            <span>
                ${record.organization || ""}
            </span>

        </div>

    `;

}


//====================================
// إغلاق نافذة التفاصيل
//====================================

if (closeModal) {

    closeModal.addEventListener("click", () => {

        modal.style.display = "none";

    });

}


window.addEventListener("click", (event) => {


    if (event.target === modal) {

        modal.style.display = "none";

    }

});


//====================================
// تعديل السجل
//====================================

function editRecord(id) {

    window.location.href =
        "/result?id=" + id;

}


//====================================
// حذف السجل
//====================================

async function deleteRecord(id) {


    const confirmDelete =
        confirm("هل أنت متأكد من حذف هذا السجل؟");


    if (!confirmDelete) {

        return;

    }


    try {


        const response =
            await fetch("/delete/" + id, {

                method: "DELETE"

            });


        const result =
            await response.json();


        alert(result.message);


        loadArchive();


    }


    catch (error) {


        console.log(error);


        alert("حدث خطأ أثناء حذف السجل");

    }

}


//====================================
// فتح ملف Word
//====================================

function openWord(id) {

    window.open(
        "/word/" + id,
        "_blank"
    );

}


//====================================
// الوضع الليلي
//====================================

function setTheme(theme) {


    if (theme === "dark") {


        document.body.classList.add("dark");


        if (darkBtn) {

            darkBtn.innerHTML =
                '<i class="fa-solid fa-sun"></i>';

        }


        if (logo) {

            logo.src =
                "/static/images/logo-dark.jpg";

        }

    }


    else {


        document.body.classList.remove("dark");


        if (darkBtn) {

            darkBtn.innerHTML =
                '<i class="fa-solid fa-moon"></i>';

        }


        if (logo) {

            logo.src =
                "/static/images/logo.jpg";

        }

    }


    localStorage.setItem("theme", theme);

}


//====================================
// تحميل الوضع المحفوظ
//====================================

const savedTheme =
    localStorage.getItem("theme");


if (savedTheme) {

    setTheme(savedTheme);

}

else {

    setTheme("light");

}


//====================================
// زر الوضع الليلي
//====================================

if (darkBtn) {


    darkBtn.addEventListener("click", () => {


        if (
            document.body.classList.contains("dark")
        ) {

            setTheme("light");

        }

        else {

            setTheme("dark");

        }

    });

}


//====================================
// تشغيل الأرشيف
//====================================

loadArchive();


//====================================
// END
//====================================

console.log(
    "✅ Bayan OCR Archive Loaded Successfully"
);