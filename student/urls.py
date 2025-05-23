from django.urls import path
from student import views
from django.contrib.auth.views import LoginView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('studentclick', views.studentclick_view, name='student-click'),
    path('studentlogin', LoginView.as_view(
        template_name='student/studentlogin.html',
        extra_context={'site_header': '🎒 Talaba Kirishi'}
    ), name='studentlogin'),
    path('studentsignup', views.student_signup_view, name='studentsignup'),

    # Social Media Redirects
    path('social/facebook/', RedirectView.as_view(url='https://facebook.com/yourpage'), name='social-facebook'),
    path('social/twitter/', RedirectView.as_view(url='https://twitter.com/yourpage'), name='social-twitter'),
    path('social/instagram/', RedirectView.as_view(url='https://instagram.com/yourpage'), name='social-instagram'),

    # Asosiy yo'nalishlar
    path('student-dashboard', views.student_dashboard_view, name='student-dashboard'),
    path('student-exam', views.student_exam_view, name='student-exam'),
    path('take-exam/<int:pk>', views.take_exam_view, name='take-exam'),
    path('start-exam/<int:pk>', views.start_exam_view, name='start-exam'),

    # Natijalar bilan ishlash
    path('calculate-marks', views.calculate_marks_view, name='calculate-marks'),
    path('view-result', views.view_result_view, name='view-result'),
    path('check-marks/<int:pk>', views.check_marks_view, name='check-marks'),
    path('student-marks', views.student_marks_view, name='student-marks'),
]