from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User

class AcademicYear(models.Model):
    year = models.CharField(max_length=9, unique=True)  
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year']
    
    def __str__(self):
        return self.year
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Ensure only one academic year is active
            AcademicYear.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

class Grade(models.Model):
    name = models.CharField(max_length=50) 
    level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['level']
        unique_together = ['name', 'level']
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    grades = models.ManyToManyField(Grade, related_name='subjects')
    is_core = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_grades_display(self):
        return ", ".join([grade.name for grade in self.grades.all()])

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'user_type': 'teacher'},
        related_name='teaching_classes'
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    max_students = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    room_number = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'academic_year']
        ordering = ['grade__level', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"
    
    @property
    def current_students_count(self):
        return self.student_set.filter(is_active=True).count()
    
    @property
    def available_spots(self):
        return self.max_students - self.current_students_count
    
    @property
    def is_full(self):
        return self.current_students_count >= self.max_students