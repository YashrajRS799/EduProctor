"""
OpenCV Webcam Monitoring Script – EduProctor
============================================
Run this as a subprocess from the server side to capture webcam frames
and report face detection results back to the Django backend via HTTP.

Usage:
    python monitoring/webcam_monitor.py --session_id 5 --student_token <token> --server http://localhost:8000

Requirements:
    pip install opencv-python requests
"""

import cv2
import time
import argparse
import requests
import sys
import os


# ── Haar Cascade path (bundled with OpenCV) ──────────────────────────────────
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


def detect_faces(frame):
    """
    Detect faces in a BGR frame using Haar Cascade classifier.
    Returns the count of detected faces.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    return len(faces), faces


def post_result(server_url, session_id, cookies, face_count, details='', violation_type=None):
    """POST face count result back to Django monitoring endpoint."""
    url = f"{server_url}/monitoring/webcam-status/"
    payload = {
        'session_id': session_id,
        'face_count': face_count,
        'details': details,
        'violation_type': violation_type,
    }
    try:
        response = requests.post(url, json=payload, cookies=cookies, timeout=3)
        return response.json()
    except requests.RequestException as e:
        print(f"[webcam_monitor] POST error: {e}", file=sys.stderr)
        return None


def run_monitor(session_id, server_url, cookies, interval=5, show_preview=False):
    """
    Main loop: capture webcam frames every `interval` seconds,
    detect faces, and report violations back to the server.
    """
    cap = cv2.VideoCapture(0)  # 0 = default camera
    if not cap.isOpened():
        print('[webcam_monitor] ERROR: Cannot open webcam.', file=sys.stderr)
        sys.exit(1)

    print(f'[webcam_monitor] Started for session {session_id}. Reporting every {interval}s.')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('[webcam_monitor] WARNING: Failed to capture frame.', file=sys.stderr)
                time.sleep(interval)
                continue

            face_count, faces = detect_faces(frame)
            identity_match = True # Placeholder for facial comparison logic

            if face_count == 0:
                violation = 'no_face'
                details = 'No face detected in frame'
            elif face_count > 1:
                violation = 'multiple_faces'
                details = f'{face_count} faces detected simultaneously'
            elif not identity_match:
                violation = 'identity_mismatch'
                details = 'Captured face does not match verification photo'
            else:
                violation = None
                details = 'Normal – single face detected'

            print(f'[webcam_monitor] Faces={face_count} | {details}')

            # Only post to server when there is a potential violation or normal check-in
            post_result(server_url, session_id, cookies, face_count, details, violation)

            # Optional live preview (dev mode only)
            if show_preview:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow('EduProctor – Webcam Monitor', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(interval)

    except KeyboardInterrupt:
        print('[webcam_monitor] Stopped by user.')
    finally:
        cap.release()
        if show_preview:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EduProctor OpenCV Webcam Monitor')
    parser.add_argument('--session_id', type=int, required=True, help='ExamSession ID')
    parser.add_argument('--server', default='http://localhost:8000', help='Django server URL')
    parser.add_argument('--csrftoken', default='', help='CSRF token for POST requests')
    parser.add_argument('--sessionid', default='', help='Django session cookie value')
    parser.add_argument('--interval', type=int, default=5, help='Seconds between checks')
    parser.add_argument('--preview', action='store_true', help='Show live webcam preview')
    args = parser.parse_args()

    cookies = {
        'csrftoken': args.csrftoken,
        'sessionid': args.sessionid,
    }

    run_monitor(
        session_id=args.session_id,
        server_url=args.server,
        cookies=cookies,
        interval=args.interval,
        show_preview=args.preview,
    )
