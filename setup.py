"""
EduProctor Setup Script
=======================
Run this once after cloning the project to set up the MySQL database,
run migrations, and optionally create a superuser.

Usage:
    python setup.py
"""
import os
import sys
import subprocess


def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(1)


BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(BASE, 'venv', 'Scripts', 'python.exe')

print("=" * 60)
print("   EduProctor – Setup Script")
print("=" * 60)
print()
print("[1] Running Django system check ...")
run(f'"{PYTHON}" manage.py check', cwd=BASE)

print("\n[2] Making migrations ...")
run(f'"{PYTHON}" manage.py makemigrations', cwd=BASE)

print("\n[3] Applying migrations ...")
run(f'"{PYTHON}" manage.py migrate', cwd=BASE)

print("\n[4] Collecting static files ...")
run(f'"{PYTHON}" manage.py collectstatic --noinput', cwd=BASE)

print("\n[5] Creating superuser (admin) ...")
print("    (You can skip with Ctrl+C and create manually later)")
try:
    run(f'"{PYTHON}" manage.py createsuperuser', cwd=BASE)
except KeyboardInterrupt:
    print("    Skipped.")

print("\n" + "=" * 60)
print("   Setup complete!")
print("   Start the server with:")
print(f"   {PYTHON} manage.py runserver")
print("=" * 60)
