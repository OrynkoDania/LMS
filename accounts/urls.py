from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Головна
    # path("", views.home, name="home"),

    # Автентифікація
    path("register/", views.register, name="register"),
    # Вхід і вихід — готові в'юхи Django, нам потрібні лише свої шаблони
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),

    # Курси та уроки
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("lessons/<int:pk>/", views.lesson_detail, name="lesson_detail"),

    # Завдання (студент)
    path("assignments/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("my-grades/", views.my_grades, name="my_grades"),

    # Оцінювання (викладач / адмін)
    path("assignments/<int:assignment_id>/submissions/", views.submission_list, name="submission_list"),
    path("submissions/<int:pk>/grade/", views.grade_submission, name="grade_submission"),
]