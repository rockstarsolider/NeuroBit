// ---------- LANGUAGE DATA ----------
const translations = {
    "en": {
        "nav_manifesto": "What Neurobit do?",
        "nav_process": "Process",
        "nav_apply": "joinUS",
        "nav_playbook": "Admission Requirements",
        "nav_learning_paths": "Learning Paths",
        "logo_text": "Neurobit",
        "join_btn": "Joint Neurobit",
        "application_intro": "Start your journey by filling in the details below and take the first step toward building your future.",
        "application_fullname_label": "Full name",
        "application_phone_label": "Phone number",
        "application_location_label": "Location",
        "application_age_label": "Age",
        "application_sop_label": "Your SOP file to join Neurobit",
        "application_guideline1": "Tell us who you are, what you’ve done, and why you want to be part of Neurobit.",
        "application_guideline2": "Be honest and transparent, and write a concise text.",
        "application_guideline3": "The SOP letter should be a maximum of 2 pages.",
        "application_guideline4": "Only pdf and docx files are excpected.",
        "application_submit": "Submit",
        "footer_copy": "© 2025 – All rights marshmallow‑reserved.",
        "footer_made": "Crafted with ❤️ for Iranian youth",

    },
    "fa": {
        "nav_manifesto": "نوروبیت چیست؟",
        "nav_process": "فرآیند رشد",
        "nav_apply": "پیوستن به برنامه",
        "nav_playbook": "شرایط پذیرش",
        "nav_learning_paths": "مسیرهای یادگیری",
        "logo_text": "نوروبیت",
        "join_btn": "به نوروبیت بپیوندید",
        "application_intro": "سفر خود را با پر کردن جزئیات زیر آغاز کنید و نخستین گام را به‌سوی ساختن آینده‌تان بردارید.",
        "application_fullname_label": "نام و نام خانوادگی",
        "application_phone_label": "شماره تماس",
        "application_location_label": "شهر",
        "application_age_label": "سن",
        "application_sop_label": "فایل SOP برای پیوستن به نوروبیت",
        "application_guideline1": "به ما بگویید چه کسی هستید، چه کرده‌اید و چرا می‌خواهید بخشی از نوروبیت باشید.",
        "application_guideline2": "صادق و شفاف باشید و متنی مختصر بنویسید.",
        "application_guideline3": "نامه SOP حداکثر باید ۲ صفحه باشد.",
        "application_guideline4": "فقط فایل های pdf و docx پذیرفته می شودند.",
        "application_submit": "ارسال",
        "footer_copy": "© ۲۰۲۵ – تمامی حقوق محفوظ است.",
        "footer_made": "ساخته شده با ❤️ برای جوانان ایران",
    }
};

let currentLang = "fa";
const langBtns = document.querySelectorAll(".lang-toggle");



function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        el.innerHTML = translations[currentLang][key] || el.innerHTML;
    });
    document.documentElement.dir = currentLang === "fa" ? "rtl" : "ltr";
    langBtns.forEach(langBtn => {
        langBtn.textContent = currentLang === "fa" ? "EN" : "FA";
    });
}

langBtns.forEach(langBtn => {
    langBtn.addEventListener("click", () => {
        currentLang = currentLang === "en" ? "fa" : "en";
        applyTranslations();
    });
});


applyTranslations(); // initial