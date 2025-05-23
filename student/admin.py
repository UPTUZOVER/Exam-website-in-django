from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'address', 'mobile')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'address', 'mobile')

    def get_full_name(self, obj):
        return obj.get_name
    get_full_name.short_description = 'To‘liq Ism'
