from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=[("student", "Student"), ("teacher", "Teacher"), ("admin", "Admin")],)