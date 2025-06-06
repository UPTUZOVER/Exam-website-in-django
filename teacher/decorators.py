# teacher/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from student.models import Student
from teacher.models import Teacher


def is_teacher(user):
    """
    Foydalanuvchi teacher ekanligini tekshirish
    """
    try:
        return bool(user.teacher)
    except:
        return False


def is_student(user):
    """
    Foydalanuvchi student ekanligini tekshirish
    """
    try:
        return bool(user.student)
    except:
        return False


def user_passes_test(test_func, login_url=None, redirect_field_name=None):
    """
    Foydalanuvchi testdan o'tadimi yo'qmi tekshiruvchi dekorator
    """

    def decorator(view_func):
        from django.contrib.auth.decorators import user_passes_test as django_user_passes_test

        actual_decorator = django_user_passes_test(
            test_func,
            login_url=login_url,
            redirect_field_name=redirect_field_name
        )
        return actual_decorator(view_func)

    return decorator


def teacher_required(view_func=None, login_url='teacherlogin'):
    """
    Teacherlar uchun maxsus dekorator
    """
    actual_decorator = user_passes_test(
        is_teacher,
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def student_required(view_func=None, login_url='studentlogin'):
    """
    Studentlar uchun maxsus dekorator
    """
    actual_decorator = user_passes_test(
        is_student,
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator