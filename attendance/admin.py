# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Count
# from .models import AttendanceRecord, AttendanceSummary

# @admin.register(AttendanceRecord)
# class AttendanceRecordAdmin(admin.ModelAdmin):
#     list_display = [
#         'student', 'date', 'status', 'subject', 'class_room', 
#         'teacher', 'time_in', 'is_notified', 'marked_at'
#     ]
#     list_filter = [
#         'status', 'date', 'subject', 'class_room', 'is_notified', 
#         'marked_at', 'class_room__grade'
#     ]
#     search_fields = [
#         'student__user__first_name', 'student__user__last_name', 
#         'student__student_id', 'remarks'
#     ]
#     readonly_fields = ['marked_at', 'updated_at']
#     raw_id_fields = ['student', 'teacher', 'marked_by']
#     date_hierarchy = 'date'
    
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('student', 'class_room', 'subject', 'teacher', 'date')
#         }),
#         ('Attendance Details', {
#             'fields': ('status', 'time_in', 'time_out', 'remarks')
#         }),
#         ('Notifications', {
#             'fields': ('is_notified',)
#         }),
#         ('Administrative', {
#             'fields': ('marked_by', 'marked_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['mark_as_notified', 'send_notifications']
    
#     def mark_as_notified(self, request, queryset):
#         updated = queryset.update(is_notified=True)
#         self.message_user(request, f"{updated} records marked as notified.")
#     mark_as_notified.short_description = "Mark as notified"
    
#     def send_notifications(self, request, queryset):
#         # Placeholder for sending notifications
#         count = queryset.filter(status__in=['absent', 'late'], is_notified=False).count()
#         self.message_user(request, f"Notifications will be sent for {count} records.")
#     send_notifications.short_description = "Send parent notifications"
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related(
#             'student__user', 'class_room', 'subject', 'teacher__user'
#         )

# @admin.register(AttendanceSummary)
# class AttendanceSummaryAdmin(admin.ModelAdmin):
#     list_display = [
#         'student', 'month', 'year', 'total_days', 'present_days', 
#         'absent_days', 'attendance_percentage', 'last_updated'
#     ]
#     list_filter = ['year', 'month', 'last_updated']
#     search_fields = ['student__user__first_name', 'student__user__last_name']
#     readonly_fields = [
#         'total_days', 'present_days', 'absent_days', 'late_days', 
#         'excused_days', 'sick_days', 'attendance_percentage', 'last_updated'
#     ]
#     raw_id_fields = ['student']
    
#     actions = ['recalculate_summaries']
    
#     def recalculate_summaries(self, request, queryset):
#         for summary in queryset:
#             summary.calculate_summary()
#         self.message_user(request, f"Recalculated {queryset.count()} summaries.")
#     recalculate_summaries.short_description = "Recalculate attendance summaries"

