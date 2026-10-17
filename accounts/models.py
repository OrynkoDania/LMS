from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Варіанти ролей: (значення в БД, назва для людини)
    ROLE_CHOICES = [
        ("student", "Студент"),
        ("teacher", "Викладач"),
        ("admin", "Адміністратор"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses_taught",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="lessons/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField()
    max_grade = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Заповнює викладач після перевірки (до того моменту — порожні)
    grade = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        # Студент може здати одне завдання лише один раз
        unique_together = ["assignment", "student"]

    def __str__(self):
        return f"{self.student.username} → {self.assignment.title}"