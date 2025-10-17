from django.contrib import admin
from django.utils.html import format_html
from .models import Teacher, TeacherSchedule, TeacherLeave

class TeacherScheduleInline(admin.TabularInline):
    model = TeacherSchedule
    extra = 0
    ordering = ['day_of_week', 'start_time']

class TeacherLeaveInline(admin.TabularInline):
    model = TeacherLeave
    extra = 0
    readonly_fields = ['applied_on', 'approved_on']
    ordering = ['-applied_on']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'get_subjects_display', 
        'qualification', 'employment_status', 'joining_date', 'is_active'
    ]
    list_filter = [
        'is_active', 'qualification', 'employment_status', 
        'joining_date', 'subjects', 'can_be_class_teacher'
    ]
    search_fields = [
        'employee_id', 'user__first_name', 'user__last_name', 
        'user__email', 'specialization', 'department'
    ]
    readonly_fields = ['employee_id', 'years_of_service', 'total_students', 'created_at', 'updated_at']
    raw_id_fields = ['user']
    filter_horizontal = ['subjects']
    inlines = [TeacherScheduleInline, TeacherLeaveInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'is_active')
        }),
        ('Professional Information', {
            'fields': (
                'subjects', 'qualification', 'specialization', 
                'experience_years', 'department'
            )
        }),
        ('Employment Information', {
            'fields': (
                'joining_date', 'employment_status', 'can_be_class_teacher'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone', 
                'emergency_contact_relation'
            )
        }),
        ('Statistics', {
            'fields': ('years_of_service', 'total_students'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('subjects')

@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day_of_week', 'start_time', 'end_time', 'subject', 'class_room']
    list_filter = ['day_of_week', 'subject', 'class_room']
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name', 'room_number']
    raw_id_fields = ['teacher']

@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = [
        'teacher', 'leave_type', 'start_date', 'end_date', 
        'duration_days', 'status', 'applied_on'
    ]
    list_filter = ['leave_type', 'status', 'applied_on', 'start_date']
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name', 'reason']
    readonly_fields = ['applied_on', 'approved_on', 'duration_days']
    raw_id_fields = ['teacher', 'approved_by']
    
    fieldsets = (
        ('Leave Information', {
            'fields': ('teacher', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'admin_comments')
        }),
        ('Administrative', {
            'fields': ('applied_on', 'approved_by', 'approved_on', 'duration_days'),
            'classes': ('collapse',)
        }),
    )