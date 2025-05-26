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

    def __init__(self, *args, **kwargs):
        super(StudentUserForm, self).__init__(*args, **kwargs)
        # Make password optional for updates
        if self.instance.pk:
            self.fields['password'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Exclude current instance from the check if updating
        if self.instance and self.instance.pk:
            users = User.objects.filter(username=username).exclude(pk=self.instance.pk)
        else:
            users = User.objects.filter(username=username)
        if users.exists():
            raise forms.ValidationError("Username is already taken. Please choose another.")
        return username

class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['address','mobile','profile_pic']

