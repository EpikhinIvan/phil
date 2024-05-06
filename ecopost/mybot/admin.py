from django.contrib import admin
from .models import UserRequest, AdminResponse

# Register your models here.

@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'full_name', 'report_category', 'report_text', 'location_lat', 'location_lon', 'time', 'report_photo', 'status']
    list_filter = ['time', 'status']

@admin.register(AdminResponse)
class AdminResponseAdmin(admin.ModelAdmin):
    list_display = ['user_request', 'admin_full_name', 'admin_response_text', 'admin_response_photo', 'response_time']
