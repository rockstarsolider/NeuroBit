// static\js\script.js
// Import libraries and attach to window object
import { animate, scroll, inView } from 'motion';
import ScrambleText from 'scramble-text';
import { PowerGlitch } from 'powerglitch';



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





// ---------- SCRAMBLE CYCLE ----------
const handleScramble = (text,  el_selector) => {
    const el = document.querySelector(el_selector);
    el.innerHTML = text;
    new ScrambleText(el).play().start();
};

function cycle(el_selector) {
    try {
        handleScramble(TEXTS[i % TEXTS.length], el_selector);
        i++; setTimeout(cycle, 5000);
    } catch (error) {
        // passs
    }   
}

