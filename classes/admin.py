from django.contrib import admin
from .models import AcademicYear, Grade, Subject, ClassRoom

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['year']
    ordering = ['-year']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'created_at']
    list_filter = ['level']
    search_fields = ['name']
    ordering = ['level']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_core', 'get_grades_display', 'created_at']
    list_filter = ['is_core', 'grades']
    search_fields = ['name', 'code']
    filter_horizontal = ['grades']
    ordering = ['name']

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'class_teacher', 'academic_year', 'current_students_count', 'max_students', 'available_spots']
    list_filter = ['grade', 'academic_year', 'class_teacher']
    search_fields = ['name', 'room_number']
    ordering = ['grade__level', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grade', 'class_teacher', 'academic_year')