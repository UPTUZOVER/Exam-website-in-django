from django.db import models
from django.core.exceptions import ValidationError

from student.models import Student

class Course(models.Model):
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
   def __str__(self):
        return self.course_name




class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField(null=True,blank=True)
    question = models.TextField(max_length=600)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    cat = (
        ('Option1', 'Option1'),
        ('Option2', 'Option2'),
        ('Option3', 'Option3'),
        ('Option4', 'Option4')
    )
    answer = models.CharField(max_length=200, choices=cat)

    @property
    def options(self):
        return [
            {'value': 'Option1', 'text': self.option1},
            {'value': 'Option2', 'text': self.option2},
            {'value': 'Option3', 'text': self.option3},
            {'value': 'Option4', 'text': self.option4}
        ]

    def save(self, *args, **kwargs):
        if not self.pk and self.course.question_set.count() >= self.course.question_number:
            raise ValidationError(f"You can only create {self.course.question_number} questions for this course.")

        # Belgilangan markni avtomatik hisoblash
        if self.course.question_number > 0:
            self.marks = self.course.total_marks / self.course.question_number
        else:
            self.marks = 0

        super().save(*args, **kwargs)







class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)  # exam yoki course bitta bo‘lsin
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
