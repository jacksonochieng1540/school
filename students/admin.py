from django.contrib import admin
from django.utils.html import format_html
from .models import Student, StudentDocument

class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'get_full_name', 'class_room', 'gender', 
        'academic_year', 'is_active', 'attendance_percentage', 'admission_date'
    ]
    list_filter = [
        'is_active', 'gender', 'class_room__grade', 'academic_year', 
        'admission_date', 'class_room'
    ]
    search_fields = [
        'student_id', 'user__first_name', 'user__last_name', 
        'user__email', 'emergency_contact_name'
    ]
    readonly_fields = ['student_id', 'created_at', 'updated_at', 'attendance_percentage']
    raw_id_fields = ['user', 'parent_guardian']
    inlines = [StudentDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'student_id', 'gender', 'is_active')
        }),
        ('Academic Information', {
            'fields': ('class_room', 'academic_year', 'admission_date', 'previous_school')
        }),
        ('Guardian Information', {
            'fields': ('parent_guardian',)
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone', 
                'emergency_contact_relation'
            )
        }),
        ('Health Information', {
            'fields': ('blood_group', 'medical_conditions')
        }),
        ('System Information', {
            'fields': ('attendance_percentage', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'class_room', 'academic_year', 'parent_guardian'
        )

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'title', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'title']
    readonly_fields = ['uploaded_at']
    raw_id_fields = ['student', 'uploaded_by']