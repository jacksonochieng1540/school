from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column
from .models import ClassRoom, Subject, Grade, AcademicYear

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'grade', 'class_teacher', 'academic_year', 'max_students', 'room_number']
        widgets = {
            'max_students': forms.NumberInput(attrs={'min': 1, 'max': 50}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Class Information',
                Row(
                    Column('name', css_class='form-group col-md-6'),
                    Column('room_number', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('grade', css_class='form-group col-md-6'),
                    Column('academic_year', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('class_teacher', css_class='form-group col-md-6'),
                    Column('max_students', css_class='form-group col-md-6'),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Class', css_class='btn btn-primary')
            )
        )

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

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name', 'level', 'description']
        widgets = {
            'level': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }