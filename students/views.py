from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.urls import reverse
from accounts.decorators import admin_required, teacher_or_admin_required
from .models import Student, StudentDocument
from .forms import StudentForm, StudentDocumentForm
from classes.models import ClassRoom, Grade
from grades.models import Grade as StudentGrade

@login_required
def student_list(request):
    students = Student.objects.select_related('user', 'class_room', 'academic_year').filter(is_active=True)
    

    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
   
    class_filter = request.GET.get('class')
    if class_filter:
        students = students.filter(class_room_id=class_filter)
    

    grade_filter = request.GET.get('grade')
    if grade_filter:
        students = students.filter(class_room__grade_id=grade_filter)
    

    gender_filter = request.GET.get('gender')
    if gender_filter:
        students = students.filter(gender=gender_filter)
    

    sort_by = request.GET.get('sort', 'user__first_name')
    if sort_by in ['user__first_name', 'user__last_name', 'student_id', 'admission_date', 'class_room__name']:
        students = students.order_by(sort_by)
    

    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'classes': ClassRoom.objects.select_related('grade').all(),
        'grades': Grade.objects.all(),
        'search_query': search_query,
        'class_filter': class_filter,
        'grade_filter': grade_filter,
        'gender_filter': gender_filter,
        'sort_by': sort_by,
        'total_students': Student.objects.filter(is_active=True).count(),
    }
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, pk):
    student = get_object_or_404(
        Student.objects.select_related('user', 'class_room', 'academic_year', 'parent_guardian'),
        pk=pk
    )
    
    
    recent_grades = StudentGrade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-graded_at')[:10]
    
    
    avg_grade = StudentGrade.objects.filter(student=student).aggregate(avg=Avg('percentage'))['avg']
    
  
    from attendance.models import AttendanceRecord
    total_attendance = AttendanceRecord.objects.filter(student=student).count()
    present_count = AttendanceRecord.objects.filter(student=student, status='present').count()
    
 
    documents = student.documents.all()[:5]
    
    context = {
        'student': student,
        'recent_grades': recent_grades,
        'avg_grade': round(avg_grade, 2) if avg_grade else 0,
        'total_attendance': total_attendance,
        'present_count': present_count,
        'attendance_percentage': round((present_count / total_attendance * 100), 2) if total_attendance > 0 else 0,
        'documents': documents,
        'can_edit': request.user.user_type == 'admin',
    }
    return render(request, 'students/student_detail.html', context)

@admin_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name} added successfully!')
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'students/add_student.html', {'form': form})

@admin_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/edit_student.html', {'form': form, 'student': student})

@teacher_or_admin_required
def student_grades(request, pk):
    student = get_object_or_404(Student, pk=pk)
    grades = StudentGrade.objects.filter(student=student).select_related('exam', 'exam__subject', 'graded_by').order_by('-graded_at')
    
    
    grades_by_subject = {}
    for grade in grades:
        subject = grade.exam.subject.name
        if subject not in grades_by_subject:
            grades_by_subject[subject] = []
        grades_by_subject[subject].append(grade)
    

    subject_averages = {}
    for subject, subject_grades in grades_by_subject.items():
        avg = sum([g.percentage for g in subject_grades]) / len(subject_grades)
        subject_averages[subject] = round(avg, 2)
    
    overall_average = sum(subject_averages.values()) / len(subject_averages) if subject_averages else 0
    
    context = {
        'student': student,
        'grades_by_subject': grades_by_subject,
        'subject_averages': subject_averages,
        'overall_average': round(overall_average, 2),
    }
    return render(request, 'students/student_grades.html', context)

@teacher_or_admin_required
def student_attendance(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    from attendance.models import AttendanceRecord
    attendance_records = AttendanceRecord.objects.filter(student=student).select_related('teacher', 'subject').order_by('-date')
    

    paginator = Paginator(attendance_records, 30)
    page_number = request.GET.get('page')
    attendance_records = paginator.get_page(page_number)
    

    from django.db.models import Count
    from django.utils import timezone
    current_year = timezone.now().year
    
    monthly_summary = AttendanceRecord.objects.filter(
        student=student,
        date__year=current_year
    ).values('date__month').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    ).order_by('date__month')
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'monthly_summary': monthly_summary,
    }
    return render(request, 'students/student_attendance.html', context)

@login_required
def upload_document(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
  
    if request.user.user_type not in ['admin'] and request.user != student.user:
        raise Http404("You don't have permission to upload documents for this student.")
    
    if request.method == 'POST':
        form = StudentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentDocumentForm()
    
    return render(request, 'students/upload_document.html', {'form': form, 'student': student})

@admin_required
def bulk_import(request):
    """Bulk import students from CSV file"""
    if request.method == 'POST':
        messages.info(request, 'Bulk import functionality coming soon!')
        return redirect('students:list')
    
    return render(request, 'students/bulk_import.html')

@login_required
def get_students_by_class(request):
    """AJAX view to get students by class"""
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(
            class_room_id=class_id, 
            is_active=True
        ).select_related('user').values('id', 'user__first_name', 'user__last_name', 'student_id')
        
        return JsonResponse({
            'students': list(students)
        })
    return JsonResponse({'students': []})
