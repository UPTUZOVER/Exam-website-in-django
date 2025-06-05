from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from . import forms, models
from exam import models as QMODEL
from django.db.models import Sum, Avg

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)  # Parolni hash qilish uchun
            user.save()
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            my_student_group, created = Group.objects.get_or_create(name='STUDENT')
            my_student_group.user_set.add(user)
            return redirect('studentlogin')  # redirect ishlatildi, URL name bo'lishi kerak
    else:
        userForm = forms.StudentUserForm()
        studentForm = forms.StudentForm()

    context = {'userForm': userForm, 'studentForm': studentForm}
    return render(request, 'student/studentsignup.html', context)
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()
from .models import *
from django.db.models import Sum, Avg

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
@login_required(login_url='studentlogin')
def student_dashboard_view(request):
    student = Student.objects.get(user=request.user)

    # Get student results
    results = QMODEL.Result.objects.filter(student=student).order_by('-date')

    # Dashboard statistics
    dashboard_stats = {
        'total_courses': QMODEL.Course.objects.count(),
        'attempted_exams': results.count(),
        'total_questions': QMODEL.Question.objects.count(),
        'total_score': results.aggregate(Sum('marks'))['marks__sum'] or 0,
        'average_score': results.aggregate(Avg('marks'))['marks__avg'] or 0,
    }

    # Upcoming exams (exclude already taken)
    attempted_ids = results.values_list('exam__id', flat=True)
    upcoming_exams = QMODEL.Course.objects.exclude(id__in=attempted_ids)

    # Recent results (last 5)
    recent_results = results[:5]

    context = {
        'stats': dashboard_stats,
        'upcoming_exams': upcoming_exams,
        'recent_results': recent_results,
    }
    return render(request, 'student/student_dashboard.html', context)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response





@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.method != 'POST':
        return redirect('student_exam')

    course_id = request.COOKIES.get('course_id')
    if not course_id:
        return redirect('student_exam')

    course = get_object_or_404(QMODEL.Course, id=course_id)
    questions = QMODEL.Question.objects.filter(course=course)
    total_marks = 0

    # POST da jo'natilgan javoblarni tekshirish
    for idx, question in enumerate(questions, start=1):
        selected_answer = request.POST.get(f'question_{idx}')
        if selected_answer == question.answer:
            total_marks += question.marks or 0

    student = get_object_or_404(Student, user=request.user)

    # Result yaratish
    QMODEL.Result.objects.create(student=student, exam=course, marks=total_marks)

    # Cookie ni o'chirish (majburiy emas, lekin yaxshi amaliyot)
    response = redirect('view-result')
    response.delete_cookie('course_id')
    return response







@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  