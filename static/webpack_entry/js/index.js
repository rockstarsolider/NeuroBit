// static\webpack_entry\js\index.js

// Import libraries and attach to window object
import { animate, scroll, inView } from 'motion';
window.animate = animate;
window.scroll = scroll;
window.inView = inView;

import ScrambleText from 'scramble-text';
window.ScrambleText = ScrambleText;

import { PowerGlitch } from 'powerglitch';
// window.PowerGlitch = PowerGlitch;
PowerGlitch.glitch('.glitch',{ playMode: 'hover' });

// import { handleScramble } from './handleScramble';

// import htmx from 'htmx.org';
// window.htmx = htmx;

import '/static/css/tailwind.css';

import 'material-symbols';


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
const handleScramble = text => {
    const el = document.querySelector(".lead-text");
    el.innerHTML = text;
    new ScrambleText(el).play().start();
};

window.handleScramble = handleScramble;