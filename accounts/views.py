from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GradeForm, ProfileForm, RegisterForm, SubmissionForm
from .models import Assignment, Course, Lesson, Submission


# ---------- Допоміжний декоратор для ролей ----------

def role_required(*roles):
    """Пускає на сторінку лише користувачів із вказаними ролями.
    Використання: @role_required("teacher", "admin")"""

    def decorator(view):
        @wraps(view)
        @login_required  # спочатку перевіряємо, що користувач увійшов
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied  # відповідь 403 «Заборонено»
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


# ---------- Головна та автентифікація ----------

def home(request):
    # Шість найновіших курсів для віджета «нові курси»
    courses = Course.objects.order_by("-created_at")[:6]
    return render(request, "lms/home.html", {"courses": courses})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # роль за замовчуванням — student
            login(request, user)  # одразу входимо під новим акаунтом
            return redirect("lms:home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        # instance=request.user — редагуємо існуючого користувача, а не створюємо нового
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect("lms:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "lms/profile.html", {"form": form})


# ---------- Курси та уроки ----------

@login_required
def course_list(request):
    courses = Course.objects.select_related("teacher")  # одним запитом підтягуємо викладачів
    return render(request, "lms/course_list.html", {"courses": courses})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # prefetch_related — підтягує модулі та їхні уроки заздалегідь, без зайвих запитів у шаблоні
    modules = course.modules.prefetch_related("lessons")
    return render(request, "lms/course_detail.html", {"course": course, "modules": modules})


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, "lms/lesson_detail.html", {"lesson": lesson})


# ---------- Завдання (студент) ----------

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    # Чи здавав цей студент уже це завдання? (.first() поверне None, якщо ні)
    submission = Submission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    form = None
    if request.user.role == "student" and submission is None:
        if request.method == "POST":
            form = SubmissionForm(request.POST)
            if form.is_valid():
                new_submission = form.save(commit=False)  # поки не зберігаємо в БД
                new_submission.assignment = assignment    # дописуємо поля, яких немає у формі
                new_submission.student = request.user
                new_submission.save()
                messages.success(request, "Роботу здано!")
                return redirect("lms:assignment_detail", pk=pk)
        else:
            form = SubmissionForm()

    context = {"assignment": assignment, "submission": submission, "form": form}
    return render(request, "lms/assignment_detail.html", context)


@role_required("student")
def my_grades(request):
    submissions = Submission.objects.filter(student=request.user).select_related("assignment")
    return render(request, "lms/my_grades.html", {"submissions": submissions})


# ---------- Оцінювання (викладач / адмін) ----------

def _can_grade(user, submission):
    """Адмін оцінює все, викладач — лише роботи зі своїх курсів."""
    if user.role == "admin":
        return True
    course = submission.assignment.lesson.module.course
    return course.teacher_id == user.id


@role_required("teacher", "admin")
def submission_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    submissions = assignment.submissions.select_related("student")
    return render(
        request,
        "lms/submission_list.html",
        {"assignment": assignment, "submissions": submissions},
    )


@role_required("teacher", "admin")
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if not _can_grade(request.user, submission):
        raise PermissionDenied

    if request.method == "POST":
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Оцінку збережено.")
            return redirect("lms:submission_list", assignment_id=submission.assignment_id)
    else:
        form = GradeForm(instance=submission)
    return render(request, "lms/grade_submission.html", {"form": form, "submission": submission})