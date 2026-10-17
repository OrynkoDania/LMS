from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Submission


class RegisterForm(UserCreationForm):
    """Форма реєстрації. Поля role тут немає навмисно:
    інакше користувач сам обрав би собі роль адміністратора."""

    class Meta(UserCreationForm.Meta):
        model = User  # наша модель замість стандартної
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    """Редагування особистих даних."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class SubmissionForm(forms.ModelForm):
    """Студент пише відповідь на завдання."""

    class Meta:
        model = Submission
        fields = ("answer",)


class GradeForm(forms.ModelForm):
    """Викладач ставить оцінку і залишає коментар."""

    class Meta:
        model = Submission
        fields = ("grade", "feedback")

    def clean_grade(self):
        # clean_<поле> викликається Django автоматично для перевірки одного поля
        grade = self.cleaned_data["grade"]
        max_grade = self.instance.assignment.max_grade
        if grade is not None and grade > max_grade:
            raise forms.ValidationError(f"Максимум для цього завдання: {max_grade}.")
        return grade