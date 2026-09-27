
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


//====================================
// عناصر البحث
//====================================

const searchName =
    document.getElementById("searchName");

const searchLetter =
    document.getElementById("searchLetter");

const searchDate =
    document.getElementById("searchDate");

const searchDepartment =
    document.getElementById("searchDepartment");


//====================================
// عناصر التقويم
//====================================

const calendarButton =
    document.getElementById("calendarButton");

const hijriCalendar =
    document.getElementById("hijriCalendar");

const calendarDays =
    document.getElementById("calendarDays");

const calendarMonth =
    document.getElementById("calendarMonth");

const calendarYear =
    document.getElementById("calendarYear");

const prevMonth =
    document.getElementById("prevMonth");

const nextMonth =
    document.getElementById("nextMonth");

const todayHijri =
    document.getElementById("todayHijri");

const closeCalendar =
    document.getElementById("closeCalendar");


//====================================
// بيانات الأرشيف
//====================================

let archiveData = [];


//====================================
// أسماء الأشهر الهجرية
//====================================

const HIJRI_MONTHS = [

    "محرم",
    "صفر",
    "ربيع الأول",
    "ربيع الثاني",
    "جمادى الأولى",
    "جمادى الآخرة",
    "رجب",
    "شعبان",
    "رمضان",
    "شوال",
    "ذو القعدة",
    "ذو الحجة"

];


//====================================
// تحويل الأرقام العربية إلى إنجليزية
//====================================

function convertArabicNumbers(value) {

    return String(value || "")
        .replace(/[٠-٩]/g, digit => {

            return "٠١٢٣٤٥٦٧٨٩"
                .indexOf(digit);

        });

}


//====================================
// تنسيق التاريخ
//====================================

function formatHijriDate(
    day,
    month,
    year
) {

    return (
        String(day).padStart(2, "0")
        + "/"
        + String(month).padStart(2, "0")
        + "/"
        + String(year)
    );

}


//====================================
// توحيد صيغة التاريخ للبحث
//====================================

function normalizeSearchDate(value) {

    if (!value) {

        return "";

    }


    value =
        convertArabicNumbers(value)
        .trim();


    // تحويل الفواصل المختلفة إلى /

    value = value.replace(
        /[-.]/g,
        "/"
    );


    const match =
        value.match(
            /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/
        );


    if (!match) {

        return value;

    }


    return formatHijriDate(

        parseInt(match[1], 10),

        parseInt(match[2], 10),

        parseInt(match[3], 10)

    );

}


//====================================
// التاريخ الهجري الحالي
//====================================

function getCurrentHijri() {

    const today =
        new Date();


    const formatter =
        new Intl.DateTimeFormat(

            "en-SA-u-ca-islamic-umalqura",

            {

                day: "numeric",

                month: "numeric",

                year: "numeric"

            }

        );


    const parts =
        formatter.formatToParts(
            today
        );


    let day = 1;

    let month = 1;

    let year = 1447;


    parts.forEach(part => {

        if (part.type === "day") {

            day =
                parseInt(
                    part.value,
                    10
                );

        }


        if (part.type === "month") {

            month =
                parseInt(
                    part.value,
                    10
                );

        }


        if (part.type === "year") {

            year =
                parseInt(
                    part.value,
                    10
                );

        }

    });


    return {

        day,
        month,
        year

    };

}


//====================================
// استخراج التاريخ الهجري من تاريخ ميلادي
//====================================

function getHijriParts(date) {

    const formatter =
        new Intl.DateTimeFormat(

            "en-SA-u-ca-islamic-umalqura",

            {

                day: "numeric",

                month: "numeric",

                year: "numeric"

            }

        );


    const parts =
        formatter.formatToParts(
            date
        );


    let day = 0;

    let month = 0;

    let year = 0;


    parts.forEach(part => {

        if (part.type === "day") {

            day =
                parseInt(
                    part.value,
                    10
                );

        }


        if (part.type === "month") {

            month =
                parseInt(
                    part.value,
                    10
                );

        }


        if (part.type === "year") {

            year =
                parseInt(
                    part.value,
                    10
                );

        }

    });


    return {

        day,
        month,
        year

    };

}


//====================================
// إيجاد التاريخ الميلادي المقابل
// للتاريخ الهجري
//====================================

function findGregorianDateForHijri(
    targetYear,
    targetMonth,
    targetDay = 1
) {

    const today =
        new Date();


    const estimated =
        new Date(
            today.getTime()
        );


    const current =
        getHijriParts(
            estimated
        );


    const monthDifference =

        (
            targetYear -
            current.year
        ) * 12

        +

        (
            targetMonth -
            current.month
        );


    estimated.setDate(

        estimated.getDate()

        +

        Math.round(
            monthDifference * 29.53059
        )

    );


    for (

        let offset = -40;

        offset <= 40;

        offset++

    ) {

        const candidate =
            new Date(
                estimated.getTime()
            );


        candidate.setDate(

            candidate.getDate()

            + offset

        );


        const hijri =
            getHijriParts(
                candidate
            );


        if (

            hijri.year === targetYear

            &&

            hijri.month === targetMonth

            &&

            hijri.day === targetDay

        ) {

            return candidate;

        }

    }


    return null;

}


//====================================
// عدد أيام الشهر الهجري
//====================================

function getHijriMonthDays(
    year,
    month
) {

    const firstDay =
        findGregorianDateForHijri(
            year,
            month,
            1
        );


    if (!firstDay) {

        return 30;

    }


    let count = 0;


    const date =
        new Date(
            firstDay.getTime()
        );


    for (

        let i = 0;

        i < 32;

        i++

    ) {

        const hijri =
            getHijriParts(
                date
            );


        if (

            hijri.year === year

            &&

            hijri.month === month

        ) {

            count++;

            date.setDate(
                date.getDate() + 1
            );

        }

        else {

            break;

        }

    }


    return count;

}


//====================================
// حالة التقويم
//====================================

const currentHijri =
    getCurrentHijri();


let calendarState = {

    month:
        currentHijri.month,

    year:
        currentHijri.year

};


//====================================
// تجهيز الأشهر
//====================================

function populateMonths() {

    if (!calendarMonth) {

        return;

    }


    calendarMonth.innerHTML = "";


    HIJRI_MONTHS.forEach(

        (monthName, index) => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                index + 1;


            option.textContent =
                monthName;


            calendarMonth.appendChild(
                option
            );

        }

    );


    calendarMonth.value =
        calendarState.month;

}


//====================================
// تجهيز السنوات
//====================================

function populateYears() {

    if (!calendarYear) {

        return;

    }


    calendarYear.innerHTML = "";


    for (

        let year = 1400;

        year <= 1600;

        year++

    ) {

        const option =
            document.createElement(
                "option"
            );


        option.value =
            year;


        option.textContent =
            year;


        calendarYear.appendChild(
            option
        );

    }


    calendarYear.value =
        calendarState.year;

}


//====================================
// رسم التقويم
//====================================

function renderCalendar() {

    if (!calendarDays) {

        return;

    }


    calendarDays.innerHTML = "";


    calendarMonth.value =
        calendarState.month;


    calendarYear.value =
        calendarState.year;


    const firstGregorian =
        findGregorianDateForHijri(

            calendarState.year,

            calendarState.month,

            1

        );


    if (!firstGregorian) {

        return;

    }


    const firstWeekDay =
        firstGregorian.getDay();


    const daysInMonth =
        getHijriMonthDays(

            calendarState.year,

            calendarState.month

        );


    // الفراغات قبل أول يوم

    for (

        let i = 0;

        i < firstWeekDay;

        i++

    ) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "calendar-day empty";


        calendarDays.appendChild(
            empty
        );

    }


    // أيام الشهر

    for (

        let day = 1;

        day <= daysInMonth;

        day++

    ) {

        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";


        button.className =
            "calendar-day";


        button.textContent =
            day;


        const buttonDate =
            formatHijriDate(

                day,

                calendarState.month,

                calendarState.year

            );


        if (

            normalizeSearchDate(
                searchDate.value
            )

            ===

            buttonDate

        ) {

            button.classList.add(
                "selected"
            );

        }


        button.addEventListener(

            "click",

            () => {

                searchDate.value =
                    buttonDate;


                closeHijriCalendar();

            }

        );


        calendarDays.appendChild(
            button
        );

    }

}


//====================================
// فتح التقويم
//====================================

function openHijriCalendar() {

    hijriCalendar.classList.add(
        "open"
    );


    hijriCalendar.setAttribute(
        "aria-hidden",
        "false"
    );


    renderCalendar();

}


//====================================
// إغلاق التقويم
//====================================

function closeHijriCalendar() {

    hijriCalendar.classList.remove(
        "open"
    );


    hijriCalendar.setAttribute(
        "aria-hidden",
        "true"
    );

}


//====================================
// زر فتح التقويم
//====================================

if (calendarButton) {

    calendarButton.addEventListener(

        "click",

        event => {

            event.stopPropagation();


            if (

                hijriCalendar.classList.contains(
                    "open"
                )

            ) {

                closeHijriCalendar();

            }

            else {

                openHijriCalendar();

            }

        }

    );

}


//====================================
// منع إغلاق التقويم عند الضغط داخله
//====================================

if (hijriCalendar) {

    hijriCalendar.addEventListener(

        "click",

        event => {

            event.stopPropagation();

        }

    );

}


//====================================
// إغلاق عند الضغط خارج التقويم
//====================================

document.addEventListener(

    "click",

    event => {

        if (

            hijriCalendar

            &&

            calendarButton

            &&

            !hijriCalendar.contains(
                event.target
            )

            &&

            !calendarButton.contains(
                event.target
            )

        ) {

            closeHijriCalendar();

        }

    }

);


//====================================
// الشهر السابق
//====================================

if (prevMonth) {

    prevMonth.addEventListener(

        "click",

        () => {

            calendarState.month--;


            if (

                calendarState.month < 1

            ) {

                calendarState.month = 12;

                calendarState.year--;

            }


            if (

                calendarState.year < 1400

            ) {

                calendarState.year = 1400;

            }


            renderCalendar();

        }

    );

}


//====================================
// الشهر التالي
//====================================

if (nextMonth) {

    nextMonth.addEventListener(

        "click",

        () => {

            calendarState.month++;


            if (

                calendarState.month > 12

            ) {

                calendarState.month = 1;

                calendarState.year++;

            }


            if (

                calendarState.year > 1600

            ) {

                calendarState.year = 1600;

            }


            renderCalendar();

        }

    );

}


//====================================
// تغيير الشهر
//====================================

if (calendarMonth) {

    calendarMonth.addEventListener(

        "change",

        () => {

            calendarState.month =
                parseInt(
                    calendarMonth.value,
                    10
                );


            renderCalendar();

        }

    );

}


//====================================
// تغيير السنة
//====================================

if (calendarYear) {

    calendarYear.addEventListener(

        "change",

        () => {

            calendarState.year =
                parseInt(
                    calendarYear.value,
                    10
                );


            renderCalendar();

        }

    );

}


//====================================
// زر اليوم
//====================================

if (todayHijri) {

    todayHijri.addEventListener(

        "click",

        () => {

            const today =
                getCurrentHijri();


            calendarState.month =
                today.month;


            calendarState.year =
                today.year;


            searchDate.value =
                formatHijriDate(

                    today.day,

                    today.month,

                    today.year

                );


            closeHijriCalendar();

        }

    );

}


//====================================
// زر إغلاق التقويم
//====================================

if (closeCalendar) {

    closeCalendar.addEventListener(

        "click",

        () => {

            closeHijriCalendar();

        }

    );

}


//====================================
// الكتابة اليدوية للتاريخ
//====================================

if (searchDate) {

    searchDate.addEventListener(

        "input",

        () => {

            let value =
                searchDate.value;


            value =
                convertArabicNumbers(
                    value
                );


            value =
                value.replace(
                    /[^\d\/\-.]/g,
                    ""
                );


            value =
                value.replace(
                    /[-.]/g,
                    "/"
                );


            searchDate.value =
                value;

        }

    );


    searchDate.addEventListener(

        "blur",

        () => {

            searchDate.value =
                normalizeSearchDate(
                    searchDate.value
                );

        }

    );

}


//====================================
// تحميل السجلات
//====================================

async function loadArchive() {

    try {

        const response =
            await fetch(
                "/archive-data"
            );


        if (!response.ok) {

            throw new Error(
                "تعذر تحميل الأرشيف"
            );

        }


        archiveData =
            await response.json();


        drawTable(
            archiveData
        );

    }

    catch (error) {

        console.log(error);


        table.innerHTML = "";


        if (recordCount) {

            recordCount.textContent =
                "0 سجل";

        }


        if (emptyMessage) {

            emptyMessage.style.display =
                "block";

        }

    }

}


//====================================
// رسم الجدول
//====================================

function drawTable(data) {

    table.innerHTML = "";


    if (recordCount) {

        recordCount.textContent =
            `${data.length} سجل`;

    }


    if (

        !data

        ||

        data.length === 0

    ) {

        if (emptyMessage) {

            emptyMessage.style.display =
                "block";

        }


        return;

    }


    if (emptyMessage) {

        emptyMessage.style.display =
            "none";

    }


    data.forEach(

        (record, index) => {

            const row =
                document.createElement(
                    "tr"
                );


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


            table.appendChild(
                row
            );

        }

    );

}


//====================================
// البحث
//====================================

if (searchBtn) {

    searchBtn.addEventListener(

        "click",

        () => {

            const name =
                searchName.value
                .trim()
                .toLowerCase();


            const letter =
                searchLetter.value
                .trim()
                .toLowerCase();


            const date =
                normalizeSearchDate(
                    searchDate.value
                )
                .toLowerCase();


            const department =
                searchDepartment.value
                .trim()
                .toLowerCase();


            const filtered =
                archiveData.filter(
                    record => {

                        const recordName =
                            String(
                                record.client_name || ""
                            )
                            .trim()
                            .toLowerCase();


                        const recordLetter =
                            String(
                                record.letter_number || ""
                            )
                            .trim()
                            .toLowerCase();


                        const recordOrganization =
                            String(
                                record.organization || ""
                            )
                            .trim()
                            .toLowerCase();


                        const recordDate =
                            normalizeSearchDate(
                                record.date || ""
                            )
                            .toLowerCase();


                        // إذا كانت خانة البحث فاضية
                        // نتجاهلها


                        const nameMatch =
                            !name

                            ||

                            recordName.includes(
                                name
                            );


                        const letterMatch =
                            !letter

                            ||

                            recordLetter.includes(
                                letter
                            );


                        const departmentMatch =
                            !department

                            ||

                            recordOrganization.includes(
                                department
                            );


                        const dateMatch =
                            !date

                            ||

                            recordDate === date;


                        return (

                            nameMatch

                            &&

                            letterMatch

                            &&

                            departmentMatch

                            &&

                            dateMatch

                        );

                    }

                );


            drawTable(
                filtered
            );

        }

    );

}


//====================================
// إعادة تعيين البحث
//====================================

if (resetBtn) {

    resetBtn.addEventListener(

        "click",

        () => {

            searchName.value = "";

            searchLetter.value = "";

            searchDate.value = "";

            searchDepartment.value = "";


            drawTable(
                archiveData
            );


            closeHijriCalendar();

        }

    );

}


//====================================
// تحديث الجدول
//====================================

if (refreshBtn) {

    refreshBtn.addEventListener(

        "click",

        () => {

            loadArchive();

        }

    );

}


//====================================
// عرض السجل
//====================================

function viewRecord(id) {

    const record =
        archiveData.find(

            item =>
                item.id === id

        );


    if (!record) {

        return;

    }


    modal.style.display =
        "flex";


    modalBody.innerHTML = `

        <div class="detail-row">

            <strong>
                اسم المواطن/ة:
            </strong>

            <span>
                ${record.client_name || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>
                رقم الخطاب:
            </strong>

            <span>
                ${record.letter_number || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>
                التاريخ:
            </strong>

            <span>
                ${record.date || ""}
            </span>

        </div>


        <div class="detail-row">

            <strong>
                الجهة:
            </strong>

            <span>
                ${record.organization || ""}
            </span>

        </div>

    `;

}


//====================================
// إغلاق النافذة
//====================================

if (closeModal) {

    closeModal.addEventListener(

        "click",

        () => {

            modal.style.display =
                "none";

        }

    );

}


window.addEventListener(

    "click",

    event => {

        if (

            event.target === modal

        ) {

            modal.style.display =
                "none";

        }

    }

);


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
        confirm(
            "هل أنت متأكد من حذف هذا السجل؟"
        );


    if (!confirmDelete) {

        return;

    }


    try {

        const response =
            await fetch(

                "/delete/" + id,

                {

                    method: "DELETE"

                }

            );


        const result =
            await response.json();


        alert(
            result.message
        );


        loadArchive();

    }

    catch (error) {

        console.log(error);


        alert(
            "حدث خطأ أثناء حذف السجل"
        );

    }

}


//====================================
// فتح Word
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

        document.body.classList.add(
            "dark"
        );


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

        document.body.classList.remove(
            "dark"
        );


        if (darkBtn) {

            darkBtn.innerHTML =
                '<i class="fa-solid fa-moon"></i>';

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


//====================================
// تحميل الوضع المحفوظ
//====================================

const savedTheme =
    localStorage.getItem(
        "theme"
    );


if (savedTheme) {

    setTheme(
        savedTheme
    );

}

else {

    setTheme(
        "light"
    );

}


//====================================
// زر الوضع الليلي
//====================================

if (darkBtn) {

    darkBtn.addEventListener(

        "click",

        () => {

            if (

                document.body.classList.contains(
                    "dark"
                )

            ) {

                setTheme(
                    "light"
                );

            }

            else {

                setTheme(
                    "dark"
                );

            }

        }

    );

}


//====================================
// تشغيل الأرشيف
//====================================

populateMonths();

populateYears();

closeHijriCalendar();

loadArchive();


//====================================
// END
//====================================

console.log(
    "✅ Bayan OCR Archive Loaded Successfully"
);