"""
Exams app models – Exam, Question, ExamSession, StudentAnswer.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Exam(models.Model):
    """Represents an exam created by an admin."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Duration in minutes")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_exams',
        limit_choices_to={'role': 'admin'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        """Check if exam is currently available to take."""
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return self.questions.count()  # 1 mark per question


class Question(models.Model):
    """A single MCQ question belonging to an exam."""
    ANSWER_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"

    def get_options(self):
        """Return list of (key, text) tuples for all options."""
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]


class ExamSession(models.Model):
    """Tracks a student's attempt at an exam."""
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('flagged', 'Flagged'),
        ('timed_out', 'Timed Out'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_violation_score = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(default=0)          # Marks obtained
    total_marks = models.IntegerField(default=0)    # Total possible marks
    
    # Identity Verification
    verification_image = models.ImageField(upload_to='verification_photos/', null=True, blank=True)
    id_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'exam')       # One attempt per student per exam
        ordering = ['-start_time']
        verbose_name = 'Exam Session'
        verbose_name_plural = 'Exam Sessions'

    def __str__(self):
        return f"{self.student.username} – {self.exam.title} ({self.status})"

    @property
    def duration_elapsed(self):
        """Seconds elapsed since exam started."""
        end = self.end_time or timezone.now()
        return int((end - self.start_time).total_seconds())

    @property
    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.score / self.total_marks) * 100, 1)


class StudentAnswer(models.Model):
    """Records what a student answered for each question."""
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'question')
        verbose_name = 'Student Answer'

    def __str__(self):
        return f"{self.session.student.username} – Q{self.question.id}: {self.selected_option}"
