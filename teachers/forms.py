from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column, HTML
from .models import Teacher, TeacherSchedule, TeacherLeave
from classes.models import Subject

User = get_user_model()


class TeacherForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Teacher
        fields = [
            'employee_id', 'subjects', 'qualification', 'specialization',
            'experience_years', 'joining_date', 'employment_status', 'department',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'can_be_class_teacher'
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'subjects': forms.CheckboxSelectMultiple(),
            'experience_years': forms.NumberInput(attrs={'min': 0, 'max': 50}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['phone_number'].initial = user.phone_number
            self.fields['address'].initial = user.address
            self.fields['date_of_birth'].initial = user.date_of_birth

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="row">'),
            HTML('<div class="col-md-6">'),
            Fieldset(
                'Personal Information',
                Row(
                    Column('first_name', css_class='form-group col-md-6'),
                    Column('last_name', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('username', css_class='form-group col-md-6'),
                    Column('email', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('date_of_birth', css_class='form-group col-md-6'),
                    Column('phone_number', css_class='form-group col-md-6'),
                ),
                'address',
            ),
            Fieldset(
                'Emergency Contact',
                Row(
                    Column('emergency_contact_name', css_class='form-group col-md-6'),
                    Column('emergency_contact_relation', css_class='form-group col-md-6'),
                ),
                'emergency_contact_phone',
            ),
            HTML('</div>'),
            HTML('<div class="col-md-6">'),
            Fieldset(
                'Professional Information',
                Row(
                    Column('employee_id', css_class='form-group col-md-6'),
                    Column('joining_date', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('qualification', css_class='form-group col-md-6'),
                    Column('employment_status', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('experience_years', css_class='form-group col-md-6'),
                    Column('department', css_class='form-group col-md-6'),
                ),
                'specialization',
                'subjects',
                'can_be_class_teacher',
            ),
            HTML('</div>'),
            HTML('</div>'),
            ButtonHolder(
                Submit('submit', 'Save Teacher', css_class='btn btn-primary'),
                HTML('<a href="{% url "teachers:list" %}" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance and self.instance.pk:
            if User.objects.exclude(pk=self.instance.user.pk).filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance and self.instance.pk:
            if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if self.instance and self.instance.pk:
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.username = self.cleaned_data['username']
            user.phone_number = self.cleaned_data['phone_number']
            user.address = self.cleaned_data['address']
            user.date_of_birth = self.cleaned_data['date_of_birth']
            if commit:
                user.save()
        else:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                user_type='teacher',
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                password='teacher123'
            )
            teacher.user = user

        if commit:
            teacher.save()
            self.save_m2m()
        return teacher


class TeacherLeaveForm(forms.ModelForm):
    class Meta:
        model = TeacherLeave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Leave Request',
                Row(
                    Column('leave_type', css_class='form-group col-md-6'),
                    Column('start_date', css_class='form-group col-md-3'),
                    Column('end_date', css_class='form-group col-md-3'),
                ),
                'reason',
            ),
            ButtonHolder(
                Submit('submit', 'Submit Leave', css_class='btn btn-primary'),
                HTML('<a href="{% url "teachers:leave_list" %}" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )


class TeacherScheduleForm(forms.ModelForm):
    class Meta:
        model = TeacherSchedule
        fields = ['teacher', 'subject', 'day_of_week', 'start_time', 'end_time', 'classroom']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'classroom': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Class Schedule',
                Row(
                    Column('teacher', css_class='form-group col-md-6'),
                    Column('subject', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('day_of_week', css_class='form-group col-md-4'),
                    Column('start_time', css_class='form-group col-md-4'),
                    Column('end_time', css_class='form-group col-md-4'),
                ),
                'classroom',
            ),
            ButtonHolder(
                Submit('submit', 'Save Schedule', css_class='btn btn-success'),
                HTML('<a href="{% url "teachers:schedule_list" %}" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )
