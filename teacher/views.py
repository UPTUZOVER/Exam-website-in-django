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




@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    total_course = QMODEL.Course.objects.count()
    total_question = QMODEL.Question.objects.count()
    total_student = SMODEL.Student.objects.count()

    # Get courses with statistics
    courses = QMODEL.Course.objects.annotate(
        total_attempts=Count('result'),
        avg_score=Avg('result__marks'),
        pass_rate=ExpressionWrapper(
            Sum(
                Case(
                    When(result__marks__gte=40, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ) * 100.0 / Count('result'),
            output_field=FloatField()
        )
    ).prefetch_related(
        Prefetch(
            'result_set',
            queryset=Result.objects.select_related('student').order_by('-marks'),
            to_attr='ordered_results'
        )
    )

    # Prepare course data with top students
    for course in courses:
        if hasattr(course, 'ordered_results') and course.ordered_results:
            course.top_student = course.ordered_results[0].student
        else:
            course.top_student = None

    recent_exams = QMODEL.Course.objects.order_by('-id')[:5]
    recent_attempts = Result.objects.select_related('student', 'exam').order_by('-date')[:10]

    # Activity log
    activities = list(chain(
        QMODEL.Course.objects.filter(created_at__isnull=False).order_by('-created_at')[:10],
        Result.objects.select_related('student').order_by('-date')[:10]
    ))
    activities.sort(key=lambda x: getattr(x, 'created_at', getattr(x, 'date', None)), reverse=True)
    avg_pass_rate = 0
    if courses:
        avg_pass_rate = sum(course.pass_rate or 0 for course in courses) / len(courses)

    context = {
        'avg_pass_rate': avg_pass_rate,
        'total_course': total_course,
        'total_question': total_question,
        'total_student': total_student,
        'courses': courses,
        'recent_exams': recent_exams,
        'recent_attempts': recent_attempts,
        'activities': activities[:10],
        'course_data': {
            'labels': [course.course_name for course in courses],
            'attempts': [course.total_attempts for course in courses],
            'scores': [course.avg_score or 0 for course in courses],
            'pass_rates': [course.pass_rate or 0 for course in courses]
        }
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
