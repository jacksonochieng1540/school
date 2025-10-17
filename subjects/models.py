from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from classes.models import Grade

# The Subject model is already defined in classes/models.py, but let's add some additional models

class SubjectTeacherAssignment(models.Model):
    """Model to track which teachers are assigned to teach which subjects in which classes"""
    subject = models.ForeignKey('classes.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    class_room = models.ForeignKey('classes.ClassRoom', on_delete=models.CASCADE)
    academic_year = models.ForeignKey('classes.AcademicYear', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['subject', 'class_room', 'academic_year']
        ordering = ['subject__name', 'class_room__name']
    
    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.subject.name} - {self.class_room.name}"

class Curriculum(models.Model):
    """Model to define curriculum for each subject and grade"""
    subject = models.ForeignKey('classes.Subject', on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    academic_year = models.ForeignKey('classes.AcademicYear', on_delete=models.CASCADE)
    
    # Curriculum details
    description = models.TextField()
    learning_objectives = models.TextField(help_text="Learning objectives for this subject")
    weekly_hours = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    
    # Assessment details
    assessment_criteria = models.TextField(blank=True)
    passing_marks = models.IntegerField(default=40, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['subject', 'grade', 'academic_year']
        ordering = ['subject__name', 'grade__level']
    
    def __str__(self):
        return f"{self.subject.name} - {self.grade.name} ({self.academic_year.year})"