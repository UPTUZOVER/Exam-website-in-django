from django.db import models
from django.core.exceptions import ValidationError

from student.models import Student

from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
import pytesseract
import openai
import os
import json
from io import BytesIO

from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
import pytesseract
import openai
import json
import logging

import logging
import json
import openai
import pytesseract

from django.core.validators import MinValueValidator, MaxValueValidator

from PIL import Image
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import logging
import json
import openai
import pytesseract
from PIL import Image, ImageEnhance
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import json
import logging
from PIL import Image, ImageEnhance
import pytesseract

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import openai  # Ensure your OpenAI key is configured


openai.api_key= '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'

class Course(models.Model):
    """
    Kurs modeli:
    - Rasm yuklash orqali avtomatik test savollari generatsiya qilish
    - Belgilangan miqdordagi savollarni saqlash
    """
    course_name = models.CharField(
        max_length=100,
        verbose_name="Kurs nomi",
        help_text="Kursning to'liq nomi"
    )

    question_number = models.PositiveIntegerField(
        verbose_name="Savollar soni",
        help_text="Maksimal test savollari soni",
        default=10
    )

    total_marks = models.PositiveIntegerField(
        verbose_name="Jami ball",
        help_text="Testning umumiy balli",
        default=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan sana"
    )

    image = models.ImageField(
        upload_to='courses/questions/',
        verbose_name="Savollar rasmi",
        help_text="Test savollarini yuklang (agar matn shaklida bo'lmasa)",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course_name} ({self.question_number} savol)"

    def clean(self):
        """Validatsiya qilish"""
        if self.question_number < 1:
            raise ValidationError("Savollar soni 1 dan kam bo'lishi mumkin emas")
        if self.total_marks < self.question_number:
            raise ValidationError("Jami ball savollar sonidan kam bo'lishi mumkin emas")

    def save(self, *args, **kwargs):
        """Saqlash va rasmni qayta ishlash"""
        self.full_clean()
        is_new = not self.pk
        super().save(*args, **kwargs)

        # Agar yangi kurs yoki rasm yangilangan bo'lsa
        if is_new and self.image:
            try:
                self.process_image_to_questions()
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Rasmni qayta ishlashda xato: {str(e)}")
                # Xatoni foydalanuvchiga ko'rsatish uchun
                raise ValidationError(f"Savollar generatsiya qilinmadi: {str(e)}")

    def process_image_to_questions(self):
        """Rasmni qayta ishlab savollar generatsiya qilish"""
        # 1. OCR orqali matnni olish
        extracted_text = self.extract_text_from_image()

        # 2. ChatGPT orqali savollarni generatsiya qilish
        questions = self.generate_questions_with_chatgpt(extracted_text)

        # 3. Savollarni bazaga saqlash
        self.save_questions(questions)

    def extract_text_from_image(self):
        """Rasmdan matnni ajratib olish (OCR)"""
        try:
            with Image.open(self.image) as img:
                # Rasm sifatini yaxshilash
                img = img.convert('L')  # Gray scale
                text = pytesseract.image_to_string(img, lang='uzb+eng')
                if not text.strip():
                    raise ValidationError("Rasmdan matn olinmadi yoki matn topilmadi")
                return text
        except Exception as e:
            raise ValidationError(f"Rasmdan matn olishda xato: {str(e)}")

    def generate_questions_with_chatgpt(self, text):
        """ChatGPT orqali sifatli savollar generatsiya qilish"""
        if not text:
            raise ValidationError("Savollar generatsiya qilish uchun matn topilmadi")

        prompt = self.get_chatgpt_prompt(text)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Siz professional test savollari generatsiya qiluvchi yordamchisiz. "
                            "Savollar aniq, tushunarli va variantlar ishonarli bo'lishi kerak. "
                            "Javoblarni so'ralgan JSON formatida qaytaring."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])

        except Exception as e:
            raise ValidationError(f"AI xizmatida xato: {str(e)}")

    def get_chatgpt_prompt(self, text):
        """ChatGPT uchun optimal promptni tayyorlash"""
        return f"""
        Quyidagi matn asosida {self.question_number} ta sifatli ko'p tanlov test savollari generatsiya qiling.

        ### Asosiy talablar:
        1. Har bir savol uchun:
           - Aniq va tushunarli savol matni (o'zbek tilida)
           - 4 ta variant (1 ta to'g'ri, 3 ta noto'g'ri)
           - To'g'ri javob (Option1, Option2, Option3 yoki Option4)
        2. Savollar matnning asosiy mazmunini qamrab olishi kerak
        3. Noto'g'ri variantlar ham mantiqiy bo'lsin
        4. Kodga oid savollar bo'lsa, to'g'ri kodni tanlashni so'rang

        ### Misol savol:
        {{
            "question": "Python-da ro'yxatni teskariga aylantirish uchun qanday metod ishlatiladi?",
            "options": [
                ".reverse()",
                ".flip()",
                ".backward()",
                ".invert()"
            ],
            "answer": "Option1"
        }}

        ### Qaytariladigan format (JSON):
        {{
            "questions": [
                {{
                    "question": "...",
                    "options": ["...", "...", "...", "..."],
                    "answer": "OptionX"
                }}
            ]
        }}

        ### Matn:
        {text[:10000]}  # Matn uzunligini cheklash
        """

    def save_questions(self, questions):
        """Generatsiya qilingan savollarni saqlash"""
        if not questions:
            raise ValidationError("Hech qanday savol generatsiya qilinmadi")

        marks_per_question = round(self.total_marks / self.question_number, 2)

        for question_data in questions[:self.question_number]:
            try:
                Question.objects.create(
                    course=self,
                    marks=marks_per_question,
                    question=question_data['question'],
                    option1=question_data['options'][0],
                    option2=question_data['options'][1],
                    option3=question_data['options'][2],
                    option4=question_data['options'][3],
                    answer=question_data['answer']
                )
            except (KeyError, IndexError) as e:
                raise ValidationError(f"Savol formati noto'g'ri: {str(e)}")
            except Exception as e:
                raise ValidationError(f"Savolni saqlashda xato: {str(e)}")


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
