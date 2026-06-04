from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.utils import timezone
from django.db.models import Avg
from students.models import Student
from teachers.models import Teacher
from classes.models import Subject, AcademicYear, ClassRoom

class ExamType(models.Model):
    """Different types of examinations"""
    name = models.CharField(max_length=50)  
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[DecimalValidator(5, 2), MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage weight in final grade calculation"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.weight}%)"

class Exam(models.Model):
    """Individual examination instances"""
    name = models.CharField(max_length=100)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    

    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(15), MaxValueValidator(300)])
    total_marks = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    
    instructions = models.TextField(blank=True)
    syllabus_covered = models.TextField(blank=True, help_text="Topics/chapters covered in this exam")
   
    is_published = models.BooleanField(default=False, help_text="Whether results are published to students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
        unique_together = ['name', 'subject', 'class_room', 'academic_year']
    
    def __str__(self):
        return f"{self.name} - {self.subject.name} ({self.class_room.name})"
    
    @property
    def is_upcoming(self):
        return self.date > timezone.now().date()
    
    @property
    def is_today(self):
        return self.date == timezone.now().date()
    
    @property
    def students_count(self):
        return self.class_room.student_set.filter(is_active=True).count()
    
    @property
    def grades_entered_count(self):
        return self.grade_set.count()
    
    @property
    def grades_completion_percentage(self):
        total = self.students_count
        entered = self.grades_entered_count
        return (entered / total * 100) if total > 0 else 0
    
    @property
    def average_score(self):
        avg = self.grade_set.aggregate(avg=Avg('marks_obtained'))['avg']
        return round(avg, 2) if avg else 0

class Grade(models.Model):
    """Individual student grades for examinations"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    remarks = models.TextField(blank=True)
    
    graded_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-graded_at']
        indexes = [
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['exam', 'marks_obtained']),
        ]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.exam.name} - {self.marks_obtained}/{self.exam.total_marks}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.marks_obtained > self.exam.total_marks:
            raise ValidationError('Marks obtained cannot exceed total marks')
    
    @property
    def percentage(self):
        return round((self.marks_obtained / self.exam.total_marks) * 100, 2)
    
    @property
    def letter_grade(self):
        percentage = self.percentage
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
    @property
    def grade_point(self):
        percentage = self.percentage
        if percentage >= 90:
            return 4.0
        elif percentage >= 80:
            return 3.7
        elif percentage >= 70:
            return 3.3
        elif percentage >= 60:
            return 3.0
        elif percentage >= 50:
            return 2.0
        elif percentage >= 40:
            return 1.0
        else:
            return 0.0
    
    @property
    def is_passing(self):
        
        return self.percentage >= 40

class ReportCard(models.Model):
    """Generated report cards for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.CharField(max_length=20, choices=[
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('annual', 'Annual'),
    ])
    

    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade_point_average = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=2, blank=True)
    
  
    class_rank = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(null=True, blank=True)
    
    
    generated_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    

    teacher_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'term']
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.term.title()} Report ({self.academic_year.year})"
    
    def calculate_grades(self):
        """Calculate and update report card grades"""
        from django.db.models import Sum, Avg
        
      
        grades = Grade.objects.filter(
            student=self.student,
            exam__academic_year=self.academic_year
        ).select_related('exam')
        
        if grades.exists():
          
            total_marks = sum(grade.exam.total_marks for grade in grades)
            marks_obtained = sum(float(grade.marks_obtained) for grade in grades)
            
            self.total_marks = total_marks
            self.marks_obtained = marks_obtained
            self.percentage = (marks_obtained / total_marks * 100) if total_marks > 0 else 0
            
           
            gpa = grades.aggregate(avg_gpa=Avg('grade_point'))['avg_gpa']
            self.grade_point_average = gpa or 0
           
            if self.percentage >= 90:
                self.overall_grade = 'A+'
            elif self.percentage >= 80:
                self.overall_grade = 'A'
            elif self.percentage >= 70:
                self.overall_grade = 'B+'
            elif self.percentage >= 60:
                self.overall_grade = 'B'
            elif self.percentage >= 50:
                self.overall_grade = 'C'
            elif self.percentage >= 40:
                self.overall_grade = 'D'
            else:
                self.overall_grade = 'F'
            
            self.save()
    
    def calculate_rank(self):
        """Calculate class rank for this student"""
      
        same_class_reports = ReportCard.objects.filter(
            student__class_room=self.student.class_room,
            academic_year=self.academic_year,
            term=self.term
        ).order_by('-percentage')
        
        self.total_students = same_class_reports.count()
        
      
        for idx, report in enumerate(same_class_reports, 1):
            if report.id == self.id:
                self.class_rank = idx
                break
        
        self.save()

class GradeComment(models.Model):
    """Predefined comments that teachers can use for grades"""
    comment = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('needs_improvement', 'Needs Improvement'),
        ('poor', 'Poor'),
    ])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'comment']
    
    def __str__(self):
        return self.comment
