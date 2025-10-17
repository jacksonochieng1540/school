from django.contrib import admin
from .models import ExamType, Exam, Grade, ReportCard, GradeComment


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "weight", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "name", "exam_type", "subject", "class_room",
        "teacher", "academic_year", "date", "start_time",
        "duration_minutes", "is_published", "students_count",
        "grades_completion_percentage", "average_score"
    ]
    list_filter = ["exam_type", "subject", "class_room", "academic_year", "is_published", "date"]
    search_fields = ["name", "instructions", "syllabus_covered"]
    raw_id_fields = ["teacher", "academic_year", "class_room", "subject"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-date", "-start_time"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "exam_type", "subject", "class_room", "teacher", "academic_year"
        )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        "student", "exam", "marks_obtained", "percentage",
        "letter_grade", "grade_point", "is_passing", "graded_by", "graded_at"
    ]
    list_filter = ["exam__subject", "exam__academic_year", "graded_at"]
    search_fields = [
        "student__user__first_name", "student__user__last_name",
        "exam__name", "exam__subject__name"
    ]
    raw_id_fields = ["student", "exam", "graded_by"]
    readonly_fields = ["graded_at", "updated_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student__user", "exam", "graded_by"
        )


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = [
        "student", "academic_year", "term",
        "total_marks", "marks_obtained", "percentage",
        "grade_point_average", "overall_grade",
        "class_rank", "total_students", "generated_at"
    ]
    list_filter = ["academic_year", "term", "overall_grade", "generated_at"]
    search_fields = [
        "student__user__first_name", "student__user__last_name",
        "academic_year__year"
    ]
    raw_id_fields = ["student", "academic_year", "generated_by"]
    readonly_fields = ["generated_at", "total_marks", "marks_obtained", "percentage", "grade_point_average"]


@admin.register(GradeComment)
class GradeCommentAdmin(admin.ModelAdmin):
    list_display = ["comment", "category", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["comment"]
    ordering = ["category", "comment"]
