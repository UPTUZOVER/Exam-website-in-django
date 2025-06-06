from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM
from django.db import models
from exam.models import Result
from itertools import chain

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Case, When, Sum, Count, Avg
from django.http import HttpResponse
from exam import models as QMODEL
from student import models as SMODEL
from exam.models import Result
from itertools import chain
from django.contrib.auth.decorators import user_passes_test

@login_required(login_url='teacherlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'teacher/admin_view_student.html',{'students':students})




@login_required(login_url='teacherlogin')
def teacher_student_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    }
    return render(request,'teacher/admin_student.html',context=dict)


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')  # yoki boshqa joyga
    return render(request, 'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Case, When, Sum, Count, Avg, ExpressionWrapper, FloatField, IntegerField
from exam import models as QMODEL
from student import models as SMODEL
from exam.models import Result
from itertools import chain
from django.db.models import Prefetch, Count, Avg, Case, When, Sum, IntegerField, FloatField
from django.db.models.functions import Coalesce
from django.db.models.expressions import ExpressionWrapper

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


# teacher/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teacher.decorators import teacher_required
from exam import models as QMODEL
from student import models as SMODEL
from django.db.models import Count, Avg, Max, Min, F, Q
import datetime
from django.db.models.functions import TruncMonth


@login_required(login_url='teacherlogin')
@teacher_required
def teacher_dashboard_view(request):
    # 1. Main statistics
    total_course = QMODEL.Course.objects.count()
    total_question = QMODEL.Question.objects.count()
    total_student = SMODEL.Student.objects.count()

    # Calculate overall average score
    overall_avg = QMODEL.Result.objects.aggregate(avg_score=Avg('marks'))['avg_score'] or 0

    # 2. Course statistics
    courses = QMODEL.Course.objects.annotate(
        student_count=Count('result__student', distinct=True),
        exam_count=Count('result', distinct=True),
        avg_score=Avg('result__marks'),
        max_score=Max('result__marks'),
        min_score=Min('result__marks')
    ).order_by('-created_at')[:10]

    # 3. Top results
    top_results = QMODEL.Result.objects.select_related('student', 'exam').order_by('-marks')[:10]

    # 4. Recent results
    recent_results = QMODEL.Result.objects.select_related('student', 'exam').order_by('-date')[:10]

    # 5. Active students
    active_students = SMODEL.Student.objects.annotate(
        exam_count=Count('result__exam', distinct=True),
        last_exam_date=Max('result__date')
    ).filter(exam_count__gt=0).order_by('-exam_count')[:10]

    # 6. Data for charts
    course_names = [course.course_name for course in courses]
    course_student_counts = [course.student_count or 0 for course in courses]

    # 7. Score distribution (fixed keys)
    score_distribution = {
        "score_90_100": QMODEL.Result.objects.filter(marks__gte=90).count(),
        "score_80_89": QMODEL.Result.objects.filter(marks__gte=80, marks__lt=90).count(),
        "score_70_79": QMODEL.Result.objects.filter(marks__gte=70, marks__lt=80).count(),
        "score_60_69": QMODEL.Result.objects.filter(marks__gte=60, marks__lt=70).count(),
        "score_50_59": QMODEL.Result.objects.filter(marks__gte=50, marks__lt=60).count(),
        "score_lt_50": QMODEL.Result.objects.filter(marks__lt=50).count(),
    }

    # 8. Monthly exam activity (fixed to handle year changes)
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=180)

    # Get exam counts per month
    monthly_activity = QMODEL.Result.objects.filter(
        date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        exam_count=Count('id')
    ).order_by('month')

    # Create a dictionary of month: count
    activity_data = {entry['month']: entry['exam_count'] for entry in monthly_activity}

    # Generate data for last 6 months
    activity_months = []
    activity_counts = []

    for i in range(6):
        month_date = today - datetime.timedelta(days=30 * i)
        month_key = month_date.replace(day=1)
        count = activity_data.get(month_key, 0)
        activity_months.append(month_key.strftime("%b %Y"))
        activity_counts.append(count)

    activity_months.reverse()
    activity_counts.reverse()

    # 9. Top courses by average score
    top_courses = QMODEL.Course.objects.annotate(
        avg_score=Avg('result__marks')
    ).exclude(avg_score=None).order_by('-avg_score')[:5]

    context = {
        'total_course': total_course,
        'total_question': total_question,
        'total_student': total_student,
        'overall_avg_score': overall_avg,

        'courses': courses,
        'top_results': top_results,
        'recent_results': recent_results,
        'active_students': active_students,

        'course_names': course_names,
        'course_student_counts': course_student_counts,
        'score_distribution': score_distribution,
        'activity_months': activity_months,
        'activity_counts': activity_counts,

        'top_courses': top_courses,
        'current_month': today.strftime("%B %Y"),
    }

    return render(request, 'teacher/teacher_dashboard.html', context)



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')
