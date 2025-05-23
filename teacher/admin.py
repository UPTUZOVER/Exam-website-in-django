from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'address', 'mobile', 'status', 'salary')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'address', 'mobile')
    list_filter = ('status',)

    def get_full_name(self, obj):
        return obj.get_name
    get_full_name.short_description = 'To‘liq Ism'
