// ---------- SCRAMBLE CYCLE ----------
// const handleScramble = text => {
//     const el = document.querySelector(".lead-text"); el.innerHTML = text;
//     new ScrambleText(el).play().start();
// };
function cycle() {
    handleScramble(TEXTS[i % TEXTS.length]);
    i++; setTimeout(cycle, 5000);
}
cycle();

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