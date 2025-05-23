from django.contrib import admin
from .models import Course, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # nechta bo‘sh forma ko‘rsatiladi
    fields = ['marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
    show_change_link = True

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'question_number', 'total_marks']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'course', 'marks']
    list_filter = ['course']
    search_fields = ['question']
