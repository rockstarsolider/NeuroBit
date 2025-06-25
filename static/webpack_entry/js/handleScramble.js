import ScrambleText from 'scramble-text';

/**
 * Scramble → reveal `text` inside the element that `selector` points to.
 * Falls back silently if the element does not exist.
 */
export function handleScramble(text, selector = '.lead-text') {
  const el = document.querySelector(selector);
  if (!el) return;
  el.innerHTML = text;
  new ScrambleText(el).play().start();
}
