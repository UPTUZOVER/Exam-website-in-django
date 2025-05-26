from django import forms
from django.contrib.auth.models import User
from .models import Student

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['password'].help_text = "Parolni faqat o'zgartirmoqchi bo'lsangiz kiriting"

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Yangilash holati uchun tekshirish
        if self.instance and self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Bu username allaqachon band qilingan!")
        else:  # Yangi yaratish holati
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Bu username allaqachon band qilingan!")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['address', 'mobile', 'profile_pic']
        widgets = {
            'mobile': forms.TextInput(attrs={'pattern':'\\+?\\d{1,13}',
                                           'title':'Telefon raqamni toʻgʻri kiriting'})
        }