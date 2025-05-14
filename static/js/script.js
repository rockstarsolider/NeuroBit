// handle theming
const root = document.documentElement;
const themeToggleBtns = document.querySelectorAll('.theme-toggle');
const savedTheme = localStorage.getItem('theme');

// ----- 1. set the initial theme --------------------------------
if (savedTheme) {
    root.dataset.theme = savedTheme;      // restores last choice
    themeToggleBtns.forEach(themeToggleBtn => {
        themeToggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    });
    
    
} else {
    root.dataset.theme = 'light';         // default
}

// ----- 2. click handler ----------------------------------------
themeToggleBtns.forEach(themeToggleBtn => {
    themeToggleBtn.addEventListener('click', () => {
        const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
        root.dataset.theme = next;
        localStorage.setItem('theme', next);
        themeToggleBtn.textContent = next === 'dark' ? '☀️' : '🌙';
    });
});



// ---------- SCRAMBLE CYCLE ----------
const handleScramble = text => {
    const el = document.querySelector(".lead-text"); el.innerHTML = text;
    new ScrambleText(el).play().start();
};
function cycle() {
    try {
        handleScramble(TEXTS[i % TEXTS.length]);
        i++; setTimeout(cycle, 5000);
    } catch (error) {
        // passs
    }
    
    
}
cycle();

// title animations
const { animate, scroll, inView } = Motion;
inView(".title_with_line", (element) => {
    new ScrambleText(element).play().start();
});

inView(".team-card", (element) => {
    animate(element, { y: 10},
        { duration: 1 });
    
});

inView(".title_with_line", (element) => {
    animate(element, { y: -10},
        { duration: 1 });
});

// ---------- MENU & GRID SPOT ----------
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        const tgt = document.querySelector(link.getAttribute("href"));
        if (tgt) tgt.scrollIntoView({ behavior: "smooth" });
        document.getElementById("mobileMenu").classList.remove("open");
    });
});
document.getElementById("openMenu").addEventListener("click", () => document.getElementById("mobileMenu").classList.add("open"));
document.getElementById("closeMenu").addEventListener("click", () => {
    document.getElementById("mobileMenu").classList.remove("open");
});

const R = document.documentElement;
function setSpot(e) {
    R.style.setProperty("--cursor-x", e.clientX + "px");
    R.style.setProperty("--cursor-y", e.clientY + "px");
}
window.addEventListener("mousemove", setSpot);
window.addEventListener("touchmove", e => setSpot(e.touches[0]));


//* ---------- TESTIMONIALS CAROUSEL ---------- */
const track   = document.querySelector('#testimonials .carousel-track');
const slides  = Array.from(track.children);
const prevBtn = document.querySelector('#testimonials .prev');
const nextBtn = document.querySelector('#testimonials .next');
const dots    = document.querySelectorAll('#testimonials .dot');
let current = 0;

function goToSlide(index) {
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === index));
    current = index;
}

prevBtn.addEventListener('click', () =>
    goToSlide((current - 1 + slides.length) % slides.length)
);
nextBtn.addEventListener('click', () =>
    goToSlide((current + 1) % slides.length)
);
dots.forEach((d, i) => d.addEventListener('click', () => goToSlide(i)));

/* Optional: swipe on touch devices */
let startX = null;
track.addEventListener('touchstart', e => (startX = e.touches[0].clientX));
track.addEventListener('touchend',   e => {
    if (startX === null) return;
    const diff = e.changedTouches[0].clientX - startX;
    if      (diff > 40) prevBtn.click();
    else if (diff < -40) nextBtn.click();
    startX = null;
});


PowerGlitch.glitch('.glitch',{ playMode: 'hover' });




// hero


