from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column, HTML
from django.utils import timezone
from .models import AttendanceRecord
from students.models import Student
from classes.models import Subject, ClassRoom


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'status', 'remarks', 'date', 'subject', 'class_room', 'teacher']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for marking attendance for multiple students"""

    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students')
        existing_attendance = kwargs.pop('existing_attendance', {})
        super().__init__(*args, **kwargs)

        for student in students:
            existing_record = existing_attendance.get(student.id)

            # Status field
            status_field_name = f'status_{student.id}'
            self.fields[status_field_name] = forms.ChoiceField(
                choices=AttendanceRecord.ATTENDANCE_CHOICES,
                initial=existing_record.status if existing_record else 'present',
                widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
                label=student.__str__(),  # show student name
            )

            # Remarks field
            remarks_field_name = f'remarks_{student.id}'
            self.fields[remarks_field_name] = forms.CharField(
                required=False,
                initial=existing_record.remarks if existing_record else '',
                widget=forms.TextInput(attrs={
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Remarks...'
                }),
                label='Remarks'
            )


class AttendanceSearchForm(forms.Form):
    """Form for searching attendance records"""
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    class_room = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(AttendanceRecord.ATTENDANCE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    student_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by student name or ID...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('date_from', css_class='form-group col-md-3'),
                Column('date_to', css_class='form-group col-md-3'),
                Column('class_room', css_class='form-group col-md-3'),
                Column('subject', css_class='form-group col-md-3'),
            ),
            Row(
                Column('status', css_class='form-group col-md-6'),
                Column('student_search', css_class='form-group col-md-6'),
            ),
            ButtonHolder(
                Submit('search', 'Search', css_class='btn btn-primary'),
                HTML('<a href="?" class="btn btn-secondary ms-2">Clear</a>')
            )
        )


class AttendanceReportForm(forms.Form):
    """Form for generating attendance reports"""
    REPORT_TYPES = (
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('student_summary', 'Student Summary'),
        ('class_summary', 'Class Summary'),
    )

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    class_room = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(),
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Leave empty to include all students"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default date range: last 30 days
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)
        self.fields['date_from'].initial = thirty_days_ago
        self.fields['date_to'].initial = today

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'report_type',
            Row(
                Column('date_from', css_class='form-group col-md-6'),
                Column('date_to', css_class='form-group col-md-6'),
            ),
            'class_room',
            'students',
            ButtonHolder(
                Submit('generate', 'Generate Report', css_class='btn btn-success')
            )
        )
