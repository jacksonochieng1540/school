from django import forms
from django.forms import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column, HTML
from .models import ExamType, Exam, Grade, ReportCard, GradeComment
from students.models import Student

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            'name', 'exam_type', 'subject', 'class_room', 'academic_year',
            'date', 'start_time', 'duration_minutes', 'total_marks',
            'instructions', 'syllabus_covered'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 15, 'max': 300, 'step': 15}),
            'total_marks': forms.NumberInput(attrs={'min': 1, 'max': 1000}),
            'instructions': forms.Textarea(attrs={'rows': 3}),
            'syllabus_covered': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if teacher:
            # Filter subjects to only those assigned to the teacher
            self.fields['subject'].queryset = teacher.subjects.all()
        
        # Set default academic year
        from classes.models import AcademicYear
        try:
            active_year = AcademicYear.objects.get(is_active=True)
            self.fields['academic_year'].initial = active_year
        except AcademicYear.DoesNotExist:
            pass
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Exam Information',
                Row(
                    Column('name', css_class='form-group col-md-8'),
                    Column('exam_type', css_class='form-group col-md-4'),
                ),
                Row(
                    Column('subject', css_class='form-group col-md-6'),
                    Column('class_room', css_class='form-group col-md-6'),
                ),
                'academic_year',
            ),
            Fieldset(
                'Schedule & Marks',
                Row(
                    Column('date', css_class='form-group col-md-4'),
                    Column('start_time', css_class='form-group col-md-4'),
                    Column('duration_minutes', css_class='form-group col-md-4'),
                ),
                'total_marks',
            ),
            Fieldset(
                'Additional Information',
                'instructions',
                'syllabus_covered',
            ),
            ButtonHolder(
                Submit('submit', 'Create Exam', css_class='btn btn-primary')
            )
        )

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'exam', 'marks_obtained', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active students and exams
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        # FIX: Remove the is_active filter since Exam model doesn't have this field
        self.fields['exam'].queryset = Exam.objects.all()  # Changed from filter(is_active=True)

class BulkGradeForm(forms.Form):
    """Form for entering grades for multiple students at once"""
    
    def __init__(self, *args, **kwargs):
        exam = kwargs.pop('exam')
        students = kwargs.pop('students')
        existing_grades = kwargs.pop('existing_grades', {})
        super().__init__(*args, **kwargs)
        
        self.exam = exam
        
        # Create fields for each student
        for student in students:
            existing_grade = existing_grades.get(student.id)
            
            # Marks field
            marks_field_name = f'marks_{student.id}'
            self.fields[marks_field_name] = forms.DecimalField(
                min_value=0,
                max_value=exam.total_marks,
                decimal_places=2,
                required=False,
                initial=existing_grade.marks_obtained if existing_grade else None,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control form-control-sm',
                    'placeholder': f'/{exam.total_marks}',
                    'step': '0.01'
                }),
                label=''
            )
            
            # Remarks field
            remarks_field_name = f'remarks_{student.id}'
            self.fields[remarks_field_name] = forms.CharField(
                required=False,
                initial=existing_grade.remarks if existing_grade else '',
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Remarks...'
                }),
                label=''
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that marks don't exceed total marks
        for field_name, value in cleaned_data.items():
            if field_name.startswith('marks_') and value is not None:
                if value > self.exam.total_marks:
                    raise forms.ValidationError(
                        f'Marks cannot exceed {self.exam.total_marks}'
                    )
        
        return cleaned_data

class ReportCardForm(forms.ModelForm):
    class Meta:
        model = ReportCard
        fields = ['student', 'academic_year', 'term', 'teacher_comments', 'principal_comments']
        widgets = {
            'teacher_comments': forms.Textarea(attrs={'rows': 3}),
            'principal_comments': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default academic year
        from classes.models import AcademicYear
        try:
            active_year = AcademicYear.objects.get(is_active=True)
            self.fields['academic_year'].initial = active_year
        except AcademicYear.DoesNotExist:
            pass
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('student', css_class='form-group col-md-6'),
                Column('term', css_class='form-group col-md-6'),
            ),
            'academic_year',
            'teacher_comments',
            'principal_comments',
            ButtonHolder(
                Submit('submit', 'Generate Report Card', css_class='btn btn-primary')
            )
        )

class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name', 'weight', 'description']
        widgets = {
            'weight': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.01}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8'),
                Column('weight', css_class='form-group col-md-4'),
            ),
            'description',
            ButtonHolder(
                Submit('submit', 'Save Exam Type', css_class='btn btn-primary')
            )
        )