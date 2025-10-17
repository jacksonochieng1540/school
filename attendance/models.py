from django.db import models
from django.utils import timezone
from students.models import Student
from teachers.models import Teacher
from classes.models import Subject, ClassRoom

class AttendanceRecord(models.Model):
    ATTENDANCE_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='present')
    remarks = models.TextField(blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date', 'subject']
        ordering = ['-date', 'student__user__first_name']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

class AttendanceSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    total_days = models.IntegerField()
    present_days = models.IntegerField()
    absent_days = models.IntegerField()
    late_days = models.IntegerField()
    
    @property
    def attendance_percentage(self):
        if self.total_days == 0:
            return 0
        return (self.present_days / self.total_days) * 100
    
    class Meta:
        unique_together = ['student', 'month', 'year']