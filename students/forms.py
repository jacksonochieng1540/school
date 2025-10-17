from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column, HTML
from .models import Student, StudentDocument
from classes.models import ClassRoom, AcademicYear

User = get_user_model()

class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'class_room', 'academic_year', 'gender', 'blood_group',
            'medical_conditions', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'admission_date', 'previous_school'
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.pop('instance_user', None)
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
        
        
        self.fields['class_room'].queryset = ClassRoom.objects.filter(
            academic_year__is_active=True
        ).select_related('grade')
        
        
        try:
            active_year = AcademicYear.objects.get(is_active=True)
            self.fields['academic_year'].initial = active_year
        except AcademicYear.DoesNotExist:
            pass
        
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
                    Column('gender', css_class='form-group col-md-6'),
                ),
                'phone_number',
                'address',
                'blood_group',
                'medical_conditions',
            ),
            HTML('</div>'),
            HTML('<div class="col-md-6">'),
            Fieldset(
                'Academic Information',
                Row(
                    Column('student_id', css_class='form-group col-md-6'),
                    Column('admission_date', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('class_room', css_class='form-group col-md-6'),
                    Column('academic_year', css_class='form-group col-md-6'),
                ),
                'previous_school',
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
            HTML('</div>'),
            ButtonHolder(
                Submit('submit', 'Save Student', css_class='btn btn-primary'),
                HTML('<a href="{% url "students:list" %}" class="btn btn-secondary ms-2">Cancel</a>')
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
    
    def clean_class_room(self):
        class_room = self.cleaned_data.get('class_room')
        if class_room and class_room.is_full:
            
            if not (self.instance and self.instance.pk and self.instance.class_room == class_room):
                raise forms.ValidationError("This class is full. Cannot assign more students.")
        return class_room
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
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
                user_type='student',
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                password='student123'  
            )
            student.user = user
        
        if commit:
            student.save()
        return student

class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['document_type', 'title', 'file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'document_type',
            'title',
            'file',
            'notes',
            ButtonHolder(
                Submit('submit', 'Upload Document', css_class='btn btn-primary')
            )
        )
