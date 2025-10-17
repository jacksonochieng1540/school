from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column
from classes.models import Subject
from .models import SubjectTeacherAssignment, Curriculum

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'grades', 'is_core']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'grades': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Subject Information',
                Row(
                    Column('name', css_class='form-group col-md-8'),
                    Column('code', css_class='form-group col-md-4'),
                ),
                'description',
                'is_core',
                'grades',
            ),
            ButtonHolder(
                Submit('submit', 'Save Subject', css_class='btn btn-primary')
            )
        )

class SubjectTeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectTeacherAssignment
        fields = ['subject', 'teacher', 'class_room', 'academic_year']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active teachers
        from teachers.models import Teacher
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).select_related('user')
        
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
                Column('subject', css_class='form-group col-md-6'),
                Column('teacher', css_class='form-group col-md-6'),
            ),
            Row(
                Column('class_room', css_class='form-group col-md-6'),
                Column('academic_year', css_class='form-group col-md-6'),
            ),
            ButtonHolder(
                Submit('submit', 'Assign Teacher', css_class='btn btn-primary')
            )
        )

class CurriculumForm(forms.ModelForm):
    class Meta:
        model = Curriculum
        fields = [
            'subject', 'grade', 'academic_year', 'description', 
            'learning_objectives', 'weekly_hours', 'assessment_criteria', 'passing_marks'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'learning_objectives': forms.Textarea(attrs={'rows': 4}),
            'assessment_criteria': forms.Textarea(attrs={'rows': 3}),
            'weekly_hours': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'passing_marks': forms.NumberInput(attrs={'min': 0, 'max': 100}),
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
            Fieldset(
                'Basic Information',
                Row(
                    Column('subject', css_class='form-group col-md-6'),
                    Column('grade', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('academic_year', css_class='form-group col-md-6'),
                    Column('weekly_hours', css_class='form-group col-md-6'),
                ),
            ),
            Fieldset(
                'Curriculum Details',
                'description',
                'learning_objectives',
            ),
            Fieldset(
                'Assessment',
                Row(
                    Column('passing_marks', css_class='form-group col-md-6'),
                ),
                'assessment_criteria',
            ),
            ButtonHolder(
                Submit('submit', 'Save Curriculum', css_class='btn btn-primary')
            )
        )