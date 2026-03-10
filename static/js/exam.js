/**
 * EduProctor – Exam Interface JS (exam.js)
 * Handles answer selections and exam submission.
 */

(function () {
    'use strict';

    // Highlight selected answer option
    document.querySelectorAll('.option-label').forEach(label => {
        label.addEventListener('click', () => {
            const name = label.htmlFor
                ? document.getElementById(label.htmlFor)?.name
                : null;
            if (name) {
                document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
                    inp.closest('.option-card')?.classList.remove('selected');
                });
            }
            label.closest('.option-card')?.classList.add('selected');
        });
    });

    // Mark radio inputs as pre-selected on page load (in case of resumption)
    document.querySelectorAll('input[type="radio"]:checked').forEach(inp => {
        inp.closest('.option-card')?.classList.add('selected');
    });

    // Confirm before submit
    const examForm = document.getElementById('exam-form');
    if (examForm) {
        examForm.addEventListener('submit', (e) => {
            const confirmed = confirm(
                'Are you sure you want to submit the exam?\nThis action cannot be undone.'
            );
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // Auto-submit when timer hits zero (triggered by timer.js via custom event)
    window.addEventListener('timerExpired', () => {
        console.warn('[EduProctor] Time expired – auto-submitting exam.');
        if (examForm) examForm.submit();
    });
})();
