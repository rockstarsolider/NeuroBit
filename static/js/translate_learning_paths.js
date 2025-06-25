// ---------- LANGUAGE DATA ----------
const translations = {
    "en": {
        "nav_manifesto": "What Neurobit do?",
        "nav_process": "Process",
        "nav_apply": "joinUS",
        "logo_text": "Neurobit",
        "join_btn": "Joint Neurobit",
        /* shared labels */
        "learning_path_title": "Learning Paths",
        "role_title": "Choose Your Role",
        "role_description": "Gain the knowledge and skills to advance in your career.",
        "if_you_like": "If you like:",
        "median_salary_label": "median salary",
        "jobs_available_label": "jobs available",
        "join_program_btn": "Join the Program",
        "program_details_btn": "Program Details",   

        "frontend_title": "Front-End Web Development",
        "frontend_summary": "Front-end developers craft the user-facing side of websites and web apps with HTML, CSS, and JavaScript—turning design mock-ups into responsive, interactive experiences.",
        "frontend_like": "designing beautiful UIs, solving UX challenges, working with React/Vue, perfecting responsive layouts",
        "frontend_salary": "$115,226",
        "frontend_jobs": "6,550",

        /* Back-End */
        "backend_title": "Back-End Web Development",
        "backend_summary": "Back-end developers build the server logic, databases, APIs, and security that power modern web applications—keeping everything fast, secure, and scalable.",
        "backend_like": "designing RESTful APIs, optimizing server performance, working with SQL/NoSQL, solving scalability puzzles",
        "backend_salary": "$150,344",
        "backend_jobs": "10,284",

        /* AI */
        "ai_title": "Artificial Intelligence",
        "ai_summary": "AI engineers design, train, and deploy machine-learning models that solve real-world problems—from predictive analytics to computer vision and natural-language understanding.",
        "ai_like": "math & statistics, Python & TensorFlow, experimenting with neural networks, turning data into smart solutions",
        "ai_salary": "$180,000",
        "ai_jobs": "9,252",

        /* Graphic Design */
        "uiux_title": "UI/UX Designer",
        "uiux_summary": "UI/UX designers craft intuitive interfaces and seamless user journeys through wireframes, prototyping, and user research.",
        "uiux_like": "user research, wireframing & prototyping, interaction design, usability testing",
        "uiux_salary": "$85,000",
        "uiux_jobs": "42,000",

        /* Game Dev */
        "game_title": "Game Development",
        "game_summary": "Game developers blend coding, design, and storytelling to build engaging experiences across PC, console, and mobile platforms with engines like Unity or Unreal.",
        "game_like": "writing game mechanics, level design, 3D assets, collaborating with artists & sound designers",
        "game_salary": "$108,471",
        "game_jobs": "53,304",

        /* UI */
        "pdq_title":"Bootcamp Path-Discovery Interest Quiz",
        "pdq_intro":"20 quick questions (≈11 min) → personal interest card.",
        "pdq_prev":"Back","pdq_next":"Next","pdq_finish":"Finish",
        "pdq_result_title":"Your Interest Card",
        "pdq_primary":"Primary Path:","pdq_secondary":"Secondary Path:",
        "pdq_see_cards":"Highlight my card",

        /* Section names */
        "pdq_secA":"A) Everyday Interests",
        "pdq_secB":"B) Problem-Solving Style",
        "pdq_secC":"C) Personal Motivation (Likert)",
        "pdq_secD":"D) Self-assessed Abilities",
        "pdq_secE":"E) Ideal Work Environment (Rank 1-5)",

        /* Likert scale ends */
        "pdq_scale1":"1 = Strongly disagree",
        "pdq_scale5":"5 = Strongly agree",

        /* Q1-Q6  (Section A) */
        "pdq_q1":"When you open a new app or website, what grabs you first?",
        "pdq_q1_a1":"Colours & layout",
        "pdq_q1_a2":"Smooth interactions",
        "pdq_q1_a3":"Where data is stored & processed",
        "pdq_q1_a4":"Guessing the algorithm behind it",
        "pdq_q1_a5":"Understanding the game mechanics",

        "pdq_q2":"If you start a personal project, you would likely …",
        "pdq_q2_a1":"Design a beautiful blog theme",
        "pdq_q2_a2":"Build a simple API to manage data",
        "pdq_q2_a3":"Train a model to classify your photos",
        "pdq_q2_a4":"Create characters & world for a mini-game",
        "pdq_q2_a5":"Draw a big canvas and digitise it",

        "pdq_q3":"Which activity sounds most attractive?",
        "pdq_q3_a1":"Experimenting with fonts & images",
        "pdq_q3_a2":"Writing code to crunch lots of data",
        "pdq_q3_a3":"Designing a fun game level",
        "pdq_q3_a4":"Hunting a logic bug in backend",
        "pdq_q3_a5":"Crafting interactive visual effects",

        "pdq_q4":"How would you like the outcome of your work to feel?",
        "pdq_q4_a1":"Eye-catching & beautiful",
        "pdq_q4_a2":"Reliable & error-free",
        "pdq_q4_a3":"Smart & self-learning",
        "pdq_q4_a4":"Fun & interactive",
        "pdq_q4_a5":"All of the above, beauty first",

        "pdq_q5":"The word “optimisation” reminds you of …",
        "pdq_q5_a1":"Reducing page-load time",
        "pdq_q5_a2":"Speeding up database queries",
        "pdq_q5_a3":"Lowering model prediction error",
        "pdq_q5_a4":"Lighter textures for higher FPS",
        "pdq_q5_a5":"Compressing images I designed",

        "pdq_q6":"In a team, you prefer to be in charge of …",
        "pdq_q6_a1":"User-interface design",
        "pdq_q6_a2":"Server-side logic",
        "pdq_q6_a3":"AI for non-player character",
        "pdq_q6_a4":"Creating characters & animation",
        "pdq_q6_a5":"Integrating all parts together",

        /* Q7-Q10  (Section B) */
        "pdq_q7":"Facing a “500 – Server Error”, you …",
        "pdq_q7_a1":"Check server logs immediately",
        "pdq_q7_a2":"Isolate reason with UI tests",
        "pdq_q7_a3":"Compare in/out data & inspect model",
        "pdq_q7_a4":"Design a creative error image",
        "pdq_q7_a5":"Turn the error into a mini-game",

        "pdq_q8":"Client wants a “user behaviour prediction” feature …",
        "pdq_q8_a1":"Research a suitable ML model",
        "pdq_q8_a2":"Write a new API to store & fetch data",
        "pdq_q8_a3":"Design how results appear in UI",
        "pdq_q8_a4":"Think how to gamify the feature",

        "pdq_q9":"User complains the app is slow. Your first focus:",
        "pdq_q9_a1":"Server & DB profiling",
        "pdq_q9_a2":"Shrink graphic assets",
        "pdq_q9_a3":"Simplify model computations",
        "pdq_q9_a4":"Reduce extra 3-D objects",

        "pdq_q10":"Your team enters a 48-hour hackathon. You …",
        "pdq_q10_a1":"Pitch a small creative game idea",
        "pdq_q10_a2":"Focus on accuracy & speed of an algorithm",
        "pdq_q10_a3":"Take care of the UI build",
        "pdq_q10_a4":"Own the database & API",
        "pdq_q10_a5":"Prepare brand style & slide deck",

        /* Q11-Q14  (Section C) */
        "pdq_q11":"I prefer my work outcome to be tangible and visual.",
        "pdq_q12":"I enjoy solving back-stage logic even if unseen.",
        "pdq_q13":"I’m excited to create fun, engaging user experiences.",
        "pdq_q14":"I’m fascinated by finding hidden patterns in data.",

        /* Q15-Q17 (Section D) */
        "pdq_q15":"I’m skilled in visual design (hand or digital).",
        "pdq_q16":"I grasp math & logic concepts easily.",
        "pdq_q17":"I convey ideas well using images & diagrams.",

        /* Q18-Q20 (Section E) */
        "pdq_q18":"A large cross-disciplinary team with strict processes",
        "pdq_q19":"A creative space with high artistic freedom",
        "pdq_q20":"A project where users/players give instant feedback",

        /* optional dynamic advice messages */
        "pdq_advice_F":"3-day challenge: rebuild a landing page with pure HTML/CSS.",
        "pdq_advice_B":"Spin up a REST API and connect it to a toy DB.",
        "pdq_advice_AI":"Try a Kaggle intro dataset and train a simple model.",
        "pdq_advice_G":"Redesign a poster in Adobe Illustrator.",
        "pdq_advice_GM":"Make a tiny platformer in Unity using free assets."
    },

    "fa": {
        "nav_manifesto": "نوروبیت چیست؟",
        "nav_process": "پروسه رشد",
        "nav_apply": "پیوستن به برنامه",
        "logo_text": "نوروبیت",
        "join_btn": "به نوروبیت بپیوندید",
        /* shared labels */
        "nav_learning_paths": "مسیرهای یادگیری",
        "role_title": "انتخاب مسیر گسب درآمد",
        "role_description": "دانش و مهارت‌های لازم برای پیشرفت را کسب کنید.",
        "if_you_like": "اگر به این‌ها علاقه دارید:",
        "median_salary_label": "حقوق متوسط در سال",
        "jobs_available_label": "شغل موجود",
        "join_program_btn": "پیوستن به برنامه",
        "program_details_btn": "جزئیات برنامه",

        "frontend_title": "توسعه وب فرانت‌اند",
        "frontend_summary": "توسعه‌دهندگان فرانت‌اند بخش قابل‌مشاهدهٔ وب‌سایت‌ها و وب‌اپ‌ها را با HTML، CSS و جاوااسکریپت می‌سازند و طرح‌های گرافیکی را به تجربه‌های واکنش‌گرا و تعاملی تبدیل می‌کنند.",
        "frontend_like": "طراحی رابط‌های زیبا، حل چالش‌های تجربه کاربری، کار با React/Vue، بهبود لایه‌بندی واکنش‌گرا",
        "frontend_salary": "حدود ۴۸۴ میلیون تومان",
        "frontend_jobs": "۶٬۵۵۰",

        /* Back-End */
        "backend_title": "توسعه وب بک‌اند",
        "backend_summary": "توسعه‌دهندگان بک‌اند منطق سرور، پایگاه‌داده‌ها، APIها و امنیت را پیاده‌سازی می‌کنند تا اپلیکیشن‌های وب سریع، ایمن و مقیاس‌پذیر باشند.",
        "backend_like": "بهینه‌سازی عملکرد سرور، ایجاد APIهای RESTful، کار با پایگاه داده، ساخت وب‌سایت‌های پویا، مقیاس‌پذیر، سریع و امن.",
        "backend_salary": "حدود ۶۳۰ میلیون تومان",
        "backend_jobs": "۱۰,۲۸۴",

        /* AI */
        "ai_title": "هوش مصنوعی",
        "ai_summary": "مهندسان هوش مصنوعی مدل‌های یادگیری ماشین را طراحی، آموزش و استقرار می‌دهند تا از تحلیل پیش‌بینانه تا بینایی ماشین و پردازش زبان طبیعی مشکلات واقعی را حل کنند.",
        "ai_like": "ریاضیات و آمار، پایتون و TensorFlow، آزمایش شبکه‌های عصبی، تبدیل داده به راهکار هوشمند",
        "ai_salary": "حدود ۷۵۶ میلیون تومان",
        "ai_jobs": "۹,۵۵۲",

        /* UI/UX Designer */
        "uiux_title": "طراح UI/UX",
        "uiux_summary": "طراحان UI/UX با استفاده از وایرفریم، پروتوتایپ و تحقیق کاربر، رابط‌های کاربرپسند و تجربه‌های بدون نقص خلق می‌کنند.",
        "uiux_like": "تحقیق کاربر، وایرفریم و پروتوتایپ، طراحی تعامل، تست قابلیت استفاده",
        "uiux_salary": "حدود ۵۳۰ میلیون تومان",
        "uiux_jobs": "۴۲٬۰۰۰",

        /* Game Dev */
        "game_title": "بازی سازی",
        "game_summary": "توسعه‌دهندگان بازی با کدنویسی، طراحی و داستان‌گویی، تجربه‌های تعاملی می‌سازند و با موتورهایی مثل Unity یا Unreal روی پلتفرم‌های PC، موبایل و کنسول بازی تولید می‌کنند.",
        "game_like": "پیاده‌سازی مکانیک‌های بازی، طراحی مراحل، ساخت دارایی‌های سه‌بعدی، همکاری با هنرمندان و طراحان صدا",
        "game_salary": "حدود ۴۵۵ میلیون تومان",
        "game_jobs": "۵۳,۳۰۴",
        /* UI */
        "pdq_title":"نمیدونی کدام مسیر برای تو مناسب هست؟",
        "pdq_intro":"۲۰ پرسش کوتاه (≈۱۱ دقیقه) → کارت علاقه‌مندی فردی.",
        "pdq_prev":"قبلی","pdq_next":"بعدی","pdq_finish":"نمایش نتایج",
        "pdq_result_title":"کارت علاقه‌مندی شما",
        "pdq_primary":"مسیر اصلی:","pdq_secondary":"مسیر پشتیبان:",
        "pdq_see_cards":"کارت مرا برجسته کن",

        "pdq_secA":"A) علایق روزمره",
        "pdq_secB":"B) سبک حل مسئله",
        "pdq_secC":"C) انگیزه‌های شخصی (لیکرت)",
        "pdq_secD":"D) توانایی‌های اولیه",
        "pdq_secE":"E) محیط کاری ایده‌آل (رتبه ۱–۵)",

        "pdq_scale1":"۱ = کاملاً مخالف",
        "pdq_scale5":"۵ = کاملاً موافق",

        /* Q1-Q6 */
        "pdq_q1":"وقتی یک اپ یا وب‌سایت جدید باز می‌کنید، چه چیزی اول توجه شما را جلب می‌کند؟",
        "pdq_q1_a1":"رنگ‌ها و چیدمان",
        "pdq_q1_a2":"سرعت و روانی تعامل",
        "pdq_q1_a3":"اینکه داده کجا ذخیره و پردازش می‌شود",
        "pdq_q1_a4":"حدس الگوریتم پشت صحنه",
        "pdq_q1_a5":"مکانیک سرگرمی چگونه کار می‌کند",

        "pdq_q2":"اگر بخواهید یک پروژه شخصی شروع کنید، احتمالاً …",
        "pdq_q2_a1":"قالب زیبایی برای وبلاگم طراحی می‌کنم",
        "pdq_q2_a2":"یک API ساده برای مدیریت دیتا می‌سازم",
        "pdq_q2_a3":"مدلی برای دسته‌بندی عکس‌هایم آموزش می‌دهم",
        "pdq_q2_a4":"کاراکتر و دنیای یک بازی کوتاه خلق می‌کنم",
        "pdq_q2_a5":"یک بوم بزرگ می‌کشم و دیجیتال می‌کنم",

        "pdq_q3":"کدام فعالیت برایتان جذاب‌تر است؟",
        "pdq_q3_a1":"آزمودن ترکیب فونت و تصویر",
        "pdq_q3_a2":"نوشتن کدی که داده زیادی پردازش کند",
        "pdq_q3_a3":"طراحی مرحله‌ای سرگرم‌کننده",
        "pdq_q3_a4":"پیداکردن خطای منطق برنامه",
        "pdq_q3_a5":"ساخت جلوه بصری تعاملی",

        "pdq_q4":"دوست دارید نتیجه کارتان چگونه دیده شود؟",
        "pdq_q4_a1":"چشمگیر و زیبا",
        "pdq_q4_a2":"پایدار و بی‌خطا",
        "pdq_q4_a3":"هوشمندانه و خودآموز",
        "pdq_q4_a4":"مفرح و تعاملی",
        "pdq_q4_a5":"همه مهم‌اند اما اول زیبایی!",

        "pdq_q5":"واژه «بهینه‌سازی» شما را یاد چه می‌اندازد؟",
        "pdq_q5_a1":"کوتاه کردن زمان بارگذاری صفحه",
        "pdq_q5_a2":"بهبود سرعت پرس‌وجوی پایگاه‌داده",
        "pdq_q5_a3":"کاهش خطای مدل پیش‌بینی",
        "pdq_q5_a4":"سبک‌تر کردن تکسچرهای بازی برای FPS بالاتر",
        "pdq_q5_a5":"فشرده‌سازی تصاویر طراحی‌شده",

        "pdq_q6":"ترجیح می‌دهید مسئول کدامیک از موارد زیر باشید؟",
        "pdq_q6_a1":"طراحی رابط کاربر",
        "pdq_q6_a2":"ساخت منطق سرور",
        "pdq_q6_a3":"پیاده‌سازی هوش شخصیت بازی",
        "pdq_q6_a4":"خلق شخصیت و انیمیشن‌ها",
        "pdq_q6_a5":"یکپارچه‌سازی همه بخش‌ها",

        /* Q7-Q10 */
        "pdq_q7":"وقتی خطای «۵۰۰ – Server Error» می‌بینید …",
        "pdq_q7_a1":"سریع لاگ‌های سرور را چک می‌کنم",
        "pdq_q7_a2":"با تست UI علت را جدا می‌کنم",
        "pdq_q7_a3":"داده ورودی/خروجی و مدل را بررسی می‌کنم",
        "pdq_q7_a4":"یک تصویر خطای خلاقانه می‌سازم",
        "pdq_q7_a5":"خطا را به مینی‌گیم تبدیل می‌کنم",

        "pdq_q8":"اگر مشتری ویژگی «پیش‌بینی رفتار کاربر» بخواهد …",
        "pdq_q8_a1":"مدل یادگیری ماشین مناسب را تحقیق می‌کنم",
        "pdq_q8_a2":"API جدید برای دیتا می‌نویسم",
        "pdq_q8_a3":"نمایش نتیجه پیش‌بینی در UI را طراحی می‌کنم",
        "pdq_q8_a4":"فکر می‌کنم چگونه آن را بازی‌گونه کنم",

        "pdq_q9":"کاربر از کندی اپلیکیشن شکایت دارد. اولویت شما:",
        "pdq_q9_a1":"پروفایلینگ سرور و دیتابیس",
        "pdq_q9_a2":"سبک‌کردن فایل‌های گرافیکی",
        "pdq_q9_a3":"ساده‌سازی محاسبات مدل",
        "pdq_q9_a4":"کاهش اشیای سه‌بعدی اضافی",

        "pdq_q10":"در هکاتون ۴۸ ساعته، شما …",
        "pdq_q10_a1":"ایده یک بازی کوچک مطرح می‌کنم",
        "pdq_q10_a2":"روی دقت و سرعت الگوریتم کار می‌کنم",
        "pdq_q10_a3":"ساخت رابط کاربر را برعهده می‌گیرم",
        "pdq_q10_a4":"مسئول دیتابیس و API می‌شوم",
        "pdq_q10_a5":"هویت بصری و ارائه را آماده می‌کنم",

        /* Q11-Q14 */
        "pdq_q11":"«ترجیح می‌دهم خروجی کارم ملموس و دیداری باشد.»",
        "pdq_q12":"«از حل چالش‌های منطقی پشت صحنه لذت می‌برم.»",
        "pdq_q13":"«هیجان دارم تجربه‌ای سرگرم‌کننده خلق کنم.»",
        "pdq_q14":"«کشف الگوهای پنهان در داده‌ها برایم جذاب است.»",

        /* Q15-Q17 */
        "pdq_q15":"«در طراحی بصری مهارت دارم.»",
        "pdq_q16":"«درک مفاهیم ریاضی و منطقی برایم ساده است.»",
        "pdq_q17":"«برای ارائه ایده‌ها با تصاویر توانمندم.»",

        /* Q18-Q20 */
        "pdq_q18":"یک تیم چندرشته‌ای بزرگ با فرآیند دقیق",
        "pdq_q19":"فضایی خلاق با آزادی هنری بالا",
        "pdq_q20":"پروژه‌ای با بازخورد لحظه‌ای کاربر/بازیکن",

        /* توصیه کوتاه */
        "pdq_advice_F":"چالش سه‌روزه: صفحه فرود سایتی را با HTML/CSS بازسازی کن.",
        "pdq_advice_B":"یک REST API ساده بنویس و به DB متصل کن.",
        "pdq_advice_AI":"در کگل یک دیتاست مقدماتی را مدل کن.",
        "pdq_advice_G":"یک پوستر در Illustrator بازطراحی کن.",
        "pdq_advice_GM":"یک پلتفرمر کوچک در Unity بساز."
        
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
