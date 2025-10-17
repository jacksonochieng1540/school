from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User
from classes.models import Subject

class Teacher(models.Model):
    QUALIFICATION_CHOICES = (
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('certificate', 'Teaching Certificate'),
    )
    
    EMPLOYMENT_STATUS_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('substitute', 'Substitute'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[RegexValidator(r"^[A-Z0-9]+, 'Employee ID must contain only uppercase letters and numbers'")]
    )
    
    # Professional Information
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES)
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    # Employment Information
    joining_date = models.DateField()
    employment_status = models.CharField(max_length=15, choices=EMPLOYMENT_STATUS_CHOICES, default='full_time')
    department = models.CharField(max_length=100, blank=True)
    
    # Contact and Emergency Information
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}, 'Enter a valid phone number'")]
    )
    emergency_contact_relation = models.CharField(max_length=50, default='Spouse')
    
    # Administrative
    is_active = models.BooleanField(default=True)
    can_be_class_teacher = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['employment_status']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.employee_id}"
    
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
    def years_of_service(self):
        today = timezone.now().date()
        return today.year - self.joining_date.year - (
            (today.month, today.day) < (self.joining_date.month, self.joining_date.day)
        )
    
    @property
    def assigned_classes(self):
        """Get classes where this teacher is the class teacher"""
        from classes.models import ClassRoom
        return ClassRoom.objects.filter(class_teacher=self.user)
    
    @property
    def total_students(self):
        """Get total number of students this teacher teaches"""
        total = 0
        for classroom in self.assigned_classes:
            total += classroom.current_students_count
        return total
    
    def get_subjects_display(self):
        return ", ".join([subject.name for subject in self.subjects.all()])
    
    def save(self, *args, **kwargs):
        # Auto-generate employee ID if not provided
        if not self.employee_id:
            year = timezone.now().year
            last_teacher = Teacher.objects.filter(
                employee_id__startswith=f'TCH{year}'
            ).order_by('employee_id').last()
            
            if last_teacher:
                last_number = int(last_teacher.employee_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.employee_id = f'TCH{year}{new_number:04d}'
        
        super().save(*args, **kwargs)

class TeacherSchedule(models.Model):
    """Model to store teacher's weekly schedule"""
    WEEKDAYS = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    classroom = models.CharField(max_length=50, blank=True, null=True) 
    day_of_week = models.CharField(max_length=10, choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_room = models.ForeignKey('classes.ClassRoom', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, blank=True)
    
    class Meta:
        unique_together = ['teacher', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')

class TeacherLeave(models.Model):
    """Model to track teacher leave requests"""
    LEAVE_TYPES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=15, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Administrative fields
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_leaves',
        limit_choices_to={'user_type': 'admin'}
    )
    approved_on = models.DateTimeField(null=True, blank=True)
    admin_comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applied_on']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError('End date must be after or equal to start date.')