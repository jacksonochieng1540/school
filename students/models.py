from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from accounts.models import User
from classes.models import ClassRoom, AcademicYear

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Student ID must contain only uppercase letters and numbers')]
    )
    
    
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    

    parent_guardian = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children', 
        limit_choices_to={'user_type': 'parent'}
    )
    
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or allergies")
    
    
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    emergency_contact_relation = models.CharField(max_length=50, default='Parent')
    
    
    admission_date = models.DateField()
    previous_school = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['class_room', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.student_id}"
    
    @property
    def full_name(self):
        return self.user.full_name
    
    @property
    def age(self):
        if self.user.date_of_birth:
            today = timezone.now().date()
            return today.year - self.user.date_of_birth.year - (
                (today.month, today.day) < (self.user.date_of_birth.month, self.user.date_of_birth.day)
            )
        return None
    
    @property
    def attendance_percentage(self):
        """Calculate attendance percentage for current academic year"""
        from attendance.models import AttendanceRecord
        total_days = AttendanceRecord.objects.filter(
            student=self,
            date__year=timezone.now().year
        ).count()
        
        if total_days == 0:
            return 0
        
        present_days = AttendanceRecord.objects.filter(
            student=self,
            status__in=['present', 'late'],
            date__year=timezone.now().year
        ).count()
        
        return round((present_days / total_days) * 100, 2)
    
    def save(self, *args, **kwargs):
        # Auto-generate student ID if not provided
        if not self.student_id:
            year = timezone.now().year
            last_student = Student.objects.filter(
                student_id__startswith=f'STU{year}'
            ).order_by('student_id').last()
            
            if last_student:
                last_number = int(last_student.student_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.student_id = f'STU{year}{new_number:04d}'
        
        super().save(*args, **kwargs)

class StudentDocument(models.Model):
    DOCUMENT_TYPES = (
        ('birth_certificate', 'Birth Certificate'),
        ('previous_transcript', 'Previous School Transcript'),
        ('medical_record', 'Medical Records'),
        ('photo', 'Student Photo'),
        ('other', 'Other'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_documents/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_document_type_display()}"
