/**
 * EduProctor – Countdown Timer (timer.js)
 * Displays remaining exam time and auto-triggers submission on expiry.
 */

(function () {
    'use strict';

    const timerDisplay = document.getElementById('exam-timer');
    if (!timerDisplay) return;

    let remainingSeconds = parseInt(timerDisplay.dataset.seconds || '0', 10);

    function formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        if (h > 0) {
            return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function updateDisplay() {
        timerDisplay.textContent = formatTime(remainingSeconds);

        // Warning states
        if (remainingSeconds <= 60) {
            timerDisplay.classList.add('timer-danger');
            timerDisplay.classList.remove('timer-warning');
        } else if (remainingSeconds <= 300) {
            timerDisplay.classList.add('timer-warning');
        }
    }

    updateDisplay();

    const interval = setInterval(() => {
        remainingSeconds--;
        updateDisplay();

        if (remainingSeconds <= 0) {
            clearInterval(interval);
            timerDisplay.textContent = '00:00';
            // Dispatch custom event caught by exam.js to trigger form submit
            window.dispatchEvent(new Event('timerExpired'));
        }
    }, 1000);
})();
