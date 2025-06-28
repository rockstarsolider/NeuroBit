// ============================  translate_pricing.js  (updated) ============================
// سوییچ بین فارسی و انگلیسی + جدول کامل متون

const translations = {
    fa: {
      "nav_manifesto": "نوروبیت چیست؟",
      "nav_process": "فرآیند رشد",
      "nav_apply": "پیوستن به برنامه",
      "nav_playbook": "شرایط پذیرش",
      "nav_learning_paths": "مسیرهای یادگیری",
      "nav_pricing": "هزینه ها",
      "nav_mentorship": "منتورشیپ",
      "join_btn": "به نوروبیت بپیوندید",
      /* --- HERO --- */
      pricing_hero_title: "پلن مناسب خود را انتخاب کنید",
      pricing_hero_subtitle: "دسترسی کامل به مسیرهای یادگیری، منتورینگ و انجمن خصوصی",
      pricing_hero_cta: "جلسهٔ معارفه رایگان",
  
      /* --- PLAN NAMES + BADGES --- */
      plan_basic_name: "نورو بیسیک",
      plan_standard_name: "نورو پلاس",
      plan_premium_name: "نورو پرو",
      plan_standard_badge: "(محبوب‌ترین)",
      plan_premium_badge: "(کامل‌ترین)",

      "plan_basic_price": "۲٬۰۰۰٬۰۰۰ تومان/ماه",
      "plan_plus_price": "۴٬۰۰۰٬۰۰۰ تومان/ماه",
      "plan_pro_price": "۸٬۰۰۰٬۰۰۰ تومان/ماه",
        
      "plan_basic_discount": "ماه اول: ۱٬۶۰۰٬۰۰۰ تومان <span class=\"chip\">%۱۵ تخفیف</span>",
      "plan_standard_discount": "ماه اول: ۳٬۲۰۰٬۰۰۰ تومان <span class=\"chip\">%۲۰ تخفیف</span>",
      "plan_premium_discount": "ماه اول: ۶٬۰۰۰٬۰۰۰ تومان <span class=\"chip\">%۲۵ تخفیف</span>",
      /* --- PLAN FEATURES (as <li> HTML) --- */
      plan_basic_features:
        "<li>مسیر یادگیری حرفه‌ای</li><li>جلسه گروهی آنلاین توسعه فردی</li><li>چت با منتور فنی و دریافت بازخورد</li><li>وبینار ماهانه والدین</li>",
      plan_standard_features:
        "<li>همه امکانات نورو بیسیک</li><li>جلسه توسعه فردی با مباحث ورزش و تغذیه</li><li>چت با منتور فنی و دریافت بازخورد</li><li>جلسه آنلاین گروهی با منتور فنی</li>",
      plan_premium_features:
        "<li>همه امکانات نورو پلاس</li><li>بازخورد و شخصی‌سازی برنامه ورزشی</li><li>مشاوره ویژه توسعه فردی</li><li>جلسه خصوصی ۶۰ دقیقه‌ای با منتور فنی</li>",
  
        "feature_matrix_title": "مقایسهٔ امکانات پلن‌ها",
      /* --- FEATURE MATRIX ROW TITLES --- */
      feature_learning_path: "مسیر یادگیری حرفه‌ای",
      feature_meta_session: "جلسه توسعه فردی (Meta)",
      feature_meta_wellness: "مباحث ورزش و تغذیه",
      feature_workout_feedback: "شخصی‌سازی برنامه ورزشی",
      feature_code_review_chat: "چت با منتور فنی",
      feature_code_review_group: "جلسه گروهی منتور فنی",
      feature_code_review_private: "جلسه خصوصی منتور فنی (۶۰ دقیقه)",
      feature_parent_webinar: "وبینار ماهانه والدین",
      feature_weekly_sessions: "برگزاری جلسات هفتگی",
  
      /* --- OTHER (نمونه) --- */
      nav_apply: "ثبت‌نام",
      "faq_title": "سؤالات متداول",
        "faq_q1": "آیا می‌توانم پلن خود را ارتقا دهم؟",
        "faq_a1": "بله، هر زمان می‌توانید با پرداخت مابه‌التفاوت ارتقا دهید.",
        "faq_q2": "تمدید اشتراک چگونه است؟",
        "faq_a2": "اشتراک هر ۳۰ روز تمدید می‌شود مگر لغو کنید.",
        "faq_q3": "اگر راضی نباشم چه؟",
        "faq_a3": "تا ۷ روز پس از ثبت نام می‌توانید کامل مبلغ را پس بگیرید.",
        "guarantee_text": "۷ روز ضمانت بازگشت وجه – بدون پرسش!",
        "final_cta_text": "هنوز مردد هستید؟ جلسهٔ معارفه رایگان را امتحان کنید.",
        "final_cta_btn": "رزرو جلسه"
    },
  
    en: {
      "nav_manifesto": "What Neurobit do?",
      "nav_process": "Process",
      "nav_apply": "joinUS",
      "nav_playbook": "Admission Requirements",
      "nav_learning_paths": "Learning Paths",
      "nav_pricing": "Pricing",
      "nav_mentorship": "Mentorship",
      "join_btn": "Joint Neurobit",
      /* --- HERO --- */
      pricing_hero_title: "Choose Your Ideal Plan",
      pricing_hero_subtitle: "Full access to learning paths, mentoring & private community",
      pricing_hero_cta: "Free intro session",
  
      /* --- PLAN NAMES + BADGES --- */
      plan_basic_name: "Neuro Basic",
      plan_standard_name: "Neuro Plus",
      plan_premium_name: "Neuro Pro",
      plan_standard_badge: "(Most popular)",
      plan_premium_badge: "(All‑inclusive)",

      "plan_basic_price": "2,000,000 Toman/month",
      "plan_standard_price": "4,000,000 Toman/month",
      "plan_pro_price": "8,000,000 Toman/month",

      "plan_basic_discount": "First month: 1,600,000 Toman <span class=\"chip\">15% off</span>",
      "plan_standard_discount": "First month: 3,200,000 Toman <span class=\"chip\">20% off</span>",
      "plan_premium_discount": "First month: 6,000,000 Toman <span class=\"chip\">25% off</span>",

  
      /* --- PLAN FEATURES (as <li> HTML) --- */
      plan_basic_features:
      "<li>Effective Learning Path</li><li>Weekly group personal‑development session</li><li>Technical mentor chat & feedback</li><li>Monthly parent webinar</li>",
      plan_standard_features:
        "<li>Everything in Basic</li><li>Broader personal‑development session (fitness & nutrition)</li><li>Technical mentor chat & feedback</li><li>Group code‑review session</li>",
      plan_premium_features:
        "<li>Everything in Plus</li><li>Personalized workout feedback</li><li>Premium personal‑development consulting</li><li>Private 60‑min code‑review session</li>",
  
        "feature_matrix_title": "Compare Plan Features",
      /* --- FEATURE MATRIX ROW TITLES --- */
      feature_learning_path: "Effective Learning Path",
      feature_meta_session: "Meta personal‑development session",
      feature_meta_wellness: "Fitness & nutrition topics",
      feature_workout_feedback: "Workout personalization",
      feature_code_review_chat: "Mentor chat feedback",
      feature_code_review_group: "Group code‑review",
      feature_code_review_private: "Private code‑review (60‑min)",
      feature_parent_webinar: "Monthly parent webinar",
      feature_weekly_sessions: "Weekly schedule",
  
      "discount_strip": "Contact us to inquire about available discounts",
    "faq_title": "Frequently Asked Questions",
    "faq_q1": "Can I upgrade my plan?",
    "faq_a1": "Yes, you can upgrade anytime by paying the difference.",
    "faq_q2": "How does subscription renewal work?",
    "faq_a2": "Your plan renews every 30 days unless cancelled.",
    "faq_q3": "What if I'm not satisfied?",
    "faq_a3": "You can request a full refund within 7 days of purchase.",
    "guarantee_text": "7-day money-back guarantee – no questions asked!",
    "final_cta_text": "Still unsure? Try our free intro session.",
    "final_cta_btn": "Book Session",
      /* --- OTHER --- */
      nav_apply: "Apply",
    },
  };
  
  // ========== Runtime translator ==========
  const langToggle = document.getElementById("langToggle");
  let currentLang = "fa";
  
  function translatePage(lang) {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (translations[lang] && translations[lang][key]) {
        el.innerHTML = translations[lang][key];
      }
    });
    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
    langToggle.textContent = lang === "fa" ? "EN" : "FA";
  }
  
  langToggle.addEventListener("click", () => {
    currentLang = currentLang === "fa" ? "en" : "fa";
    translatePage(currentLang);
  });
  
  // initial render
  translatePage(currentLang);
  