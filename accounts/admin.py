from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Module, Lesson, Assignment, Submission


# Кастомного користувача краще реєструвати через UserAdmin:
# так пароль хешується правильно, а форма виглядає як стандартна.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # додаємо наше поле role до форми редагування
    fieldsets = UserAdmin.fieldsets + (
        ("Роль", {"fields": ("role",)}),
    )
    # додаємо role до форми створення нового користувача
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Роль", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "created_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "grade", "submitted_at")
    list_filter = ("assignment",)


# Решту моделей реєструємо просто
admin.site.register([Module, Lesson, Assignment])