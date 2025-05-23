from django import forms
from django.contrib.auth.models import User
from .models import *
from exam import models as QMODEL

from django import forms
from django.contrib.auth.models import User

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Bu username allaqachon ro'yxatdan o'tgan. Iltimos, boshqa username kiriting."
            )
        return username


class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['address','mobile','profile_pic']

