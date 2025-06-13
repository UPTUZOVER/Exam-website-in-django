from rest_framework import serializers
from .models import Course, Question


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField(read_only=True)
    marks = serializers.FloatField(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'course',
            'marks',
            'question',
            'option1',
            'option2',
            'option3',
            'option4',
            'answer',
            'options'
        ]

    def get_options(self, obj):
        return obj.options

    def validate(self, data):
        course = data.get('course')
        if course and course.question_set.count() >= course.question_number:
            raise serializers.ValidationError(
                f"You can only create {course.question_number} questions for this course."
            )
        return data




class CourseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True, source='question_set')
    class Meta:
        model = Course
        fields = ["course_name", "question_number", "total_marks","created_at","questions"]
