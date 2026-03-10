# EduProctor – Online Examination Monitoring & Integrity System

A production-ready Django web application for online exam management with AI-powered proctoring using OpenCV and JavaScript behavioral monitoring.

---

## 🎯 Project Objectives

- **Secure Platform**: Develop a secure platform for conducting and monitoring online examinations.
- **Identity Verification**: Verify candidate identity before and during the exam session.
- **Live Activity Monitoring**: Monitor live exam activity using AI-based behavior analysis.
- **Behavioral Detection**: Detect tab switching, screen changes, and suspicious activities.
- **Violation Recording**: Automatically flag and record exam rule violations.
- **Scoring Engine**: Calculate violation severity using a scoring engine.
- **Integrity Reporting**: Generate integrity reports for exam administrators.

---

## ⚠️ Limitations

- **Internet Stability**: Requires a stable internet connection for uninterrupted monitoring.
- **AI Accuracy**: AI-based behavior detection may produce false positives in rare cases.
- **Hardware Dependent**: System performance depends on hardware and camera quality.
- **Lighting Conditions**: Advanced facial recognition accuracy may vary in low-light conditions.
- **Online Only**: Not suitable for offline examinations.

---

## 🚀 Scope of Future Application

- **Advanced Biometrics**: Integration with advanced facial recognition and biometric verification.
- **National Scale**: Support for large-scale national-level online examinations.
- **Cloud Scalability**: Cloud-based deployment for enhanced scalability.
- **Mobile Support**: Native mobile application support for remote exams.
- **LMS Integration**: Seamless integration with Learning Management Systems (LMS).
- **Real-time Alerts**: Real-time alert system for administrators during violations.



## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MySQL 8.0+ (running locally)
- Git

### 1. Create MySQL Database
```sql
-- Run in MySQL Workbench or MySQL CLI
CREATE DATABASE eduproctor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure Database Password
Edit `eduproctor/settings.py` and set your MySQL password:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eduproctor',
        'USER': 'root',
        'PASSWORD': 'YOUR_MYSQL_PASSWORD',  # ← change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Run Setup
```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies (already done if venv exists)
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start server
python manage.py runserver
```

### 4. Open in Browser
```
http://localhost:8000
```

---

## 📁 Project Structure

```
EduProctor/
├── eduproctor/         # Django project config
│   ├── settings.py     # MySQL, installed apps, auth
│   └── urls.py         # Root URL dispatcher
│
├── accounts/           # Auth + User model (Admin/Student roles)
│   ├── models.py       # Custom User with role field
│   ├── views.py        # Login, register, dashboards
│   ├── forms.py        # LoginForm, RegisterForm
│   └── urls.py
│
├── exams/              # Exam CRUD + student sessions
│   ├── models.py       # Exam, Question, ExamSession, StudentAnswer
│   ├── views.py        # Create exam, add questions, start exam, submit
│   ├── forms.py        # ExamForm, QuestionFormSet
│   └── urls.py
│
├── monitoring/         # Violation tracking engine
│   ├── models.py       # Violation model
│   ├── views.py        # AJAX log_violation, webcam_status endpoints
│   ├── scoring.py      # Severity map + risk level calculator
│   ├── webcam_monitor.py  # Standalone OpenCV script
│   └── urls.py
│
├── reports/            # Integrity report generation
│   ├── models.py       # IntegrityReport (OneToOne → ExamSession)
│   ├── views.py        # Report detail, list, CSV export
│   ├── utils.py        # generate_integrity_report()
│   └── urls.py
│
├── templates/          # All HTML templates
│   ├── base.html       # Sidebar layout base
│   ├── accounts/       # login, register, dashboards
│   ├── exams/          # create, questions, interface, list, detail
│   └── reports/        # report_detail, report_list
│
├── static/
│   ├── css/style.css   # Full custom CSS (dark sidebar, exam UI)
│   └── js/
│       ├── monitoring.js  # Tab/resize/fullscreen/copy detection
│       ├── exam.js        # Answer selection + submit handling
│       └── timer.js       # Countdown timer
│
├── requirements.txt
├── setup.py            # One-shot setup helper
└── manage.py
```

---

## 🔒 Security Features

| Feature | Implementation |
|---------|---------------|
| CSRF Protection | Django middleware, all POST forms |
| Session Auth | Django sessions (1-hour expiry) |
| Role-based Access | `is_admin_user` / `is_student_user` checks |
| Right-click Disable | JavaScript `contextmenu` prevention |
| Copy/Paste Block | JS `copy`, `paste`, `cut` event prevention |
| Fullscreen Enforce | JS Fullscreen API + re-prompt on exit |
| Tab Switch Detection | `visibilitychange` + `blur` events |
| Dev Tools Block | F12 / Ctrl+Shift+I keyboard block |

---

## 🎯 Violation Severity Map

| Violation | Score |
|-----------|-------|
| Multiple Faces | +10 |
| No Face Detected | +7 |
| Tab Switch | +5 |
| Fullscreen Exit | +5 |
| Copy/Paste | +4 |
| Window Resize | +3 |
| Right Click | +2 |

**Risk Levels:**
- 🟢 Low Risk: 0–20 points
- 🟡 Medium Risk: 21–50 points
- 🔴 High Risk: 51+ points

---

## 📸 OpenCV Webcam Monitor

Run as a separate process during an exam:

```bash
python monitoring/webcam_monitor.py \
  --session_id 5 \
  --server http://localhost:8000 \
  --csrftoken <token> \
  --sessionid <session_cookie> \
  --interval 5
```

Detects:
- No face in frame
- Multiple faces simultaneously
- Runs every 5 seconds (configurable)

---

## 📊 Admin Features

- **Dashboard**: Stats overview — exams, students, flagged sessions
- **Exam Management**: Create exams, add MCQ questions with inline formset
- **Reports**: View all integrity reports, filter by exam, export CSV
- **Django Admin**: Full model admin at `/admin/`

---

## 🎓 Student Features

- **Dashboard**: Available / upcoming / past exam cards
- **Exam Interface**: Full-screen, timed, monitored MCQ exam
- **Results**: Instant score + integrity report after submission
>>>>>>> 63e0d14 (Initial commit: add EduProctor project source)
