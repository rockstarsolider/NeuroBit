// static\webpack_entry\js\index.js

// Import libraries and attach to window object
import { animate, scroll, inView } from 'motion';
window.animate = animate;
window.scroll = scroll;
window.inView = inView;

import ScrambleText from 'scramble-text';
window.ScrambleText = ScrambleText;

import { PowerGlitch } from 'powerglitch';

PowerGlitch.glitch('.glitch',{ playMode: 'hover' });

import '/static/css/tailwind.css';

import 'material-symbols';

import Alpine from "alpinejs";
window.Alpine = Alpine;
Alpine.start();

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