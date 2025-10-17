from django.contrib import admin
from classes.models import Subject
from .models import SubjectTeacherAssignment, Curriculum

# Subject is already registered in classes/admin.py

@admin.register(SubjectTeacherAssignment)
class SubjectTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ['subject', 'teacher', 'class_room', 'academic_year', 'is_active']
    list_filter = ['subject', 'academic_year', 'is_active', 'class_room__grade']
    search_fields = ['subject__name', 'teacher__user__first_name', 'teacher__user__last_name', 'class_room__name']
    raw_id_fields = ['teacher']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'subject', 'teacher__user', 'class_room', 'academic_year'
        )

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['subject', 'grade', 'academic_year', 'weekly_hours', 'passing_marks']
    list_filter = ['subject', 'grade', 'academic_year']
    search_fields = ['subject__name', 'grade__name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'grade', 'academic_year', 'weekly_hours')
        }),
        ('Curriculum Details', {
            'fields': ('description', 'learning_objectives')
        }),
        ('Assessment', {
            'fields': ('assessment_criteria', 'passing_marks')
        }),
    )