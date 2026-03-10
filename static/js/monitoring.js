/**
 * EduProctor – Exam Monitoring Engine (monitoring.js)
 * =====================================================
 * Detects behavioral violations during an exam session and reports
 * them to the Django backend via AJAX.
 *
 * Violations detected:
 *   - Tab switching (visibilitychange + blur/focus)
 *   - Window resize
 *   - Fullscreen exit
 *   - Copy/paste attempts
 *   - Right-click attempts
 */

(function () {
    'use strict';

    // ── Configuration ─────────────────────────────────────────────────
    const SESSION_ID = window.EXAM_SESSION_ID;          // Set in template
    const LOG_URL = '/monitoring/log/';
    const CSRF_TOKEN = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] || '';

    // Minimum gap between same-type violations (ms) to debounce rapid fires
    const DEBOUNCE_MAP = {};
    const DEBOUNCE_INTERVAL = 3000;  // 3 seconds

    // ── Core: send violation to backend ──────────────────────────────
    function logViolation(type, details = '') {
        const now = Date.now();
        if (DEBOUNCE_MAP[type] && (now - DEBOUNCE_MAP[type]) < DEBOUNCE_INTERVAL) {
            return;  // Debounce – don't flood the server
        }
        DEBOUNCE_MAP[type] = now;

        console.warn(`[EduProctor Monitor] Violation: ${type} – ${details}`);

        fetch(LOG_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                violation_type: type,
                details: details,
            }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'ok') {
                showViolationAlert(type, data.total_score);
            }
        })
        .catch(err => console.error('[Monitor] AJAX error:', err));
    }

    // ── UI: show a non-dismissable violation toast ────────────────────
    function showViolationAlert(type, score) {
        const container = document.getElementById('violation-alert-container');
        if (!container) return;

        const label = type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const div = document.createElement('div');
        div.className = 'violation-toast';
        div.innerHTML = `⚠️ Violation detected: <strong>${label}</strong> &nbsp;|&nbsp; Score: ${score}`;
        container.appendChild(div);

        setTimeout(() => div.remove(), 4000);
    }

    // ── 1. Tab switching via Page Visibility API ───────────────────────
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            logViolation('tab_switch', 'Student switched to another tab or minimized window.');
        }
    });

    // ── 2. Window blur (alt-tab, clicking outside browser) ────────────
    window.addEventListener('blur', () => {
        logViolation('tab_switch', 'Window lost focus (blur event).');
    });

    // ── 3. Window resize ──────────────────────────────────────────────
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            logViolation('window_resize', `Window resized to ${window.innerWidth}x${window.innerHeight}.`);
        }, 500);
    });

    // ── 4. Fullscreen monitoring ───────────────────────────────────────
    function requestFullscreen() {
        const el = document.documentElement;
        if (el.requestFullscreen) el.requestFullscreen();
        else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        else if (el.mozRequestFullScreen) el.mozRequestFullScreen();
    }

    function isFullscreen() {
        return !!(
            document.fullscreenElement ||
            document.webkitFullscreenElement ||
            document.mozFullScreenElement
        );
    }

    // Enforce fullscreen on load
    window.addEventListener('load', () => {
        setTimeout(requestFullscreen, 500);
    });

    document.addEventListener('fullscreenchange', () => {
        if (!isFullscreen()) {
            logViolation('fullscreen_exit', 'Student exited fullscreen mode.');
            // Re-prompt fullscreen after a short delay
            setTimeout(requestFullscreen, 1500);
        }
    });

    document.addEventListener('webkitfullscreenchange', () => {
        if (!isFullscreen()) {
            logViolation('fullscreen_exit', 'Student exited fullscreen mode (webkit).');
            setTimeout(requestFullscreen, 1500);
        }
    });

    // ── 5. Copy/paste prevention ───────────────────────────────────────
    document.addEventListener('copy', (e) => {
        e.preventDefault();
        logViolation('copy_paste', 'Copy attempt blocked.');
    });

    document.addEventListener('paste', (e) => {
        e.preventDefault();
        logViolation('copy_paste', 'Paste attempt blocked.');
    });

    document.addEventListener('cut', (e) => {
        e.preventDefault();
        logViolation('copy_paste', 'Cut attempt blocked.');
    });

    // ── 6. Right-click prevention ──────────────────────────────────────
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        logViolation('right_click', 'Right-click context menu blocked.');
    });

    // ── 7. Keyboard shortcut blocking ─────────────────────────────────
    document.addEventListener('keydown', (e) => {
        // Block F12, Ctrl+Shift+I, Ctrl+U (developer tools / view source)
        if (
            e.key === 'F12' ||
            (e.ctrlKey && e.shiftKey && e.key === 'I') ||
            (e.ctrlKey && e.key === 'u') ||
            (e.ctrlKey && e.key === 'U')
        ) {
            e.preventDefault();
            logViolation('tab_switch', `Blocked keyboard shortcut: ${e.key}`);
        }
    });

    console.info('[EduProctor Monitor] Monitoring active for session', SESSION_ID);
})();
