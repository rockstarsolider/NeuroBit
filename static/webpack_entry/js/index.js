import '../../../input.css';

import 'material-symbols';
import 'htmx.org';
import 'htmx-ext-ws'

import Alpine from "alpinejs";
window.Alpine = Alpine;
Alpine.start();

// Notification count (header)
let numberSpan = document.getElementById("notification-number")
document.body.addEventListener('htmx:wsAfterMessage', (e) => {
    let numberOfNotifs = numberSpan.innerHTML;
    numberSpan.classList.remove('hidden')
    if (!numberOfNotifs){
        numberSpan.innerHTML = 1;
    } else {
        numberSpan.innerHTML = parseInt(numberOfNotifs) + 1;
    }
})