from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from accounts.decorators import admin_required, teacher_or_admin_required
from .models import ExamType, Exam, Grade, ReportCard, GradeComment
from .forms import ExamForm, BulkGradeForm, ReportCardForm, ExamTypeForm
from students.models import Student
from teachers.models import Teacher

@login_required
def grade_list(request):
    grades = Grade.objects.select_related('student__user', 'exam__subject', 'exam__class_room', 'graded_by__user')
    
    
    if request.user.user_type == 'teacher':
        grades = grades.filter(graded_by__user=request.user)
    elif request.user.user_type == 'student':
     
        if hasattr(request.user, 'student'):
            grades = grades.filter(student__user=request.user)
        else:
            messages.error(request, "Student profile not found. Please contact administrator.")
            grades = Grade.objects.none()
    
    
    search_query = request.GET.get('search')
    if search_query:
        grades = grades.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query) |
            Q(exam__name__icontains=search_query)
        )
    
   
    subject_filter = request.GET.get('subject')
    if subject_filter:
        grades = grades.filter(exam__subject_id=subject_filter)
    
    exam_type_filter = request.GET.get('exam_type')
    if exam_type_filter:
        grades = grades.filter(exam__exam_type_id=exam_type_filter)
    
    class_filter = request.GET.get('class')
    if class_filter:
        grades = grades.filter(exam__class_room_id=class_filter)
    
   
    paginator = Paginator(grades, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    from classes.models import Subject, ClassRoom
    from django.contrib import messages
    context = {
        'grades': page_obj,
        'subjects': Subject.objects.all(),
        'exam_types': ExamType.objects.filter(is_active=True),
        'classes': ClassRoom.objects.all(),
        'search_query': search_query,
        'subject_filter': subject_filter,
        'exam_type_filter': exam_type_filter,
        'class_filter': class_filter,
    }
    return render(request, 'grades/grade_list.html', context)
@login_required
def exam_list(request):
    """List all exams"""
    exams = Exam.objects.select_related('exam_type', 'subject', 'class_room', 'teacher__user', 'academic_year')
    
  
    if request.user.user_type == 'teacher':
        exams = exams.filter(teacher__user=request.user)
    elif request.user.user_type == 'student':
        exams = exams.filter(class_room=request.user.student.class_room)
    
    
    search_query = request.GET.get('search')
    if search_query:
        exams = exams.filter(
            Q(name__icontains=search_query) |
            Q(subject__name__icontains=search_query)
        )
    
    subject_filter = request.GET.get('subject')
    if subject_filter:
        exams = exams.filter(subject_id=subject_filter)

    status_filter = request.GET.get('status')
    today = timezone.now().date()
    if status_filter == 'upcoming':
        exams = exams.filter(date__gt=today)
    elif status_filter == 'completed':
        exams = exams.filter(date__lt=today)
    elif status_filter == 'today':
        exams = exams.filter(date=today)
    
    exams = exams.order_by('-date', '-start_time')
    
   
    paginator = Paginator(exams, 15)
    page_number = request.GET.get('page')
    exams = paginator.get_page(page_number)
    
    from classes.models import Subject
    context = {
        'exams': exams,
        'subjects': Subject.objects.all(),
        'search_query': search_query,
        'subject_filter': subject_filter,
        'status_filter': status_filter,
    }
    return render(request, 'grades/exam_list.html', context)

@teacher_or_admin_required
def create_exam(request):
    """Create a new exam"""
    teacher = None
    if request.user.user_type == 'teacher':
        
        if hasattr(request.user, 'teacher'):
            teacher = request.user.teacher
        else:
            messages.error(request, "Teacher profile not found. Please contact administrator.")
            return redirect('grades:exam_list')
    
    if request.method == 'POST':
        form = ExamForm(request.POST, teacher=teacher)
        if form.is_valid():
            exam = form.save(commit=False)
            if teacher:
                exam.teacher = teacher
            exam.save()
            messages.success(request, f'Exam "{exam.name}" created successfully!')
            return redirect('grades:exam_detail', pk=exam.pk)
    else:
        form = ExamForm(teacher=teacher)
    
    return render(request, 'grades/create_exam.html', {'form': form})

@login_required
def exam_detail(request, pk):
    """Exam detail view"""
    exam = get_object_or_404(Exam.objects.select_related('exam_type', 'subject', 'class_room', 'teacher__user'), pk=pk)
    
    grades = Grade.objects.filter(exam=exam).select_related('student__user', 'graded_by__user').order_by('student__user__first_name')
    
    
    stats = {
        'total_students': exam.students_count,
        'grades_entered': grades.count(),
        'average_score': exam.average_score,
        'highest_score': grades.aggregate(highest=models.Max('marks_obtained'))['highest'] or 0,
        'lowest_score': grades.aggregate(lowest=models.Min('marks_obtained'))['lowest'] or 0,
    }
    
  
    grade_distribution = {}
    for grade in grades:
        letter_grade = grade.letter_grade
        grade_distribution[letter_grade] = grade_distribution.get(letter_grade, 0) + 1
    
    context = {
        'exam': exam,
        'grades': grades,
        'stats': stats,
        'grade_distribution': grade_distribution,
        'can_edit': request.user.user_type in ['admin'] or (request.user.user_type == 'teacher' and exam.teacher.user == request.user),
    }
    return render(request, 'grades/exam_detail.html', context)

@teacher_or_admin_required
def enter_grades(request, exam_pk):
    """Enter grades for an exam"""
    exam = get_object_or_404(Exam, pk=exam_pk)
    
    if request.user.user_type == 'teacher' and exam.teacher.user != request.user:
        messages.error(request, "You can only enter grades for your own exams.")
        return redirect('grades:exam_list')
    
    
    students = Student.objects.filter(
        class_room=exam.class_room, 
        is_active=True
    ).select_related('user').order_by('user__first_name', 'user__last_name')
    
    existing_grades = {
        grade.student_id: grade 
        for grade in Grade.objects.filter(exam=exam)
    }
    
    if request.method == 'POST':
        form = BulkGradeForm(request.POST, exam=exam, students=students, existing_grades=existing_grades)
        if form.is_valid():
            grader = request.user.teacher if request.user.user_type == 'teacher' else Teacher.objects.first()
            saved_count = 0
            
            for student in students:
                marks_key = f'marks_{student.id}'
                remarks_key = f'remarks_{student.id}'
                
                marks = form.cleaned_data.get(marks_key)
                remarks = form.cleaned_data.get(remarks_key, '')
                
                if marks is not None:
                    grade, created = Grade.objects.update_or_create(
                        student=student,
                        exam=exam,
                        defaults={
                            'marks_obtained': marks,
                            'remarks': remarks,
                            'graded_by': grader,
                        }
                    )
                    saved_count += 1
            
            messages.success(request, f'Grades saved for {saved_count} students!')
            return redirect('grades:exam_detail', pk=exam.pk)
    else:
        form = BulkGradeForm(exam=exam, students=students, existing_grades=existing_grades)
    
    context = {
        'exam': exam,
        'form': form,
        'students': students,
        'existing_grades': existing_grades,
    }
    return render(request, 'grades/enter_grades.html', context)

@teacher_or_admin_required
def add_grade(request):
    """Add individual grade for a student"""
    from students.models import Student
    from .forms import GradeForm
    
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            
            
            if request.user.user_type == 'teacher' and hasattr(request.user, 'teacher'):
                grade.graded_by = request.user.teacher
            
            grade.save()
            messages.success(request, f'Grade added successfully for {grade.student.user.get_full_name()}!')
            return redirect('grades:list')
    else:
        form = GradeForm()
    
    
    recent_students = Student.objects.filter(is_active=True).select_related('user')[:10]
    
    context = {
        'form': form,
        'recent_students': recent_students,
        'title': 'Add Grade'
    }
    return render(request, 'grades/add_grade.html', context)

@login_required
def my_grades(request):
    """Student view of their own grades"""
    if request.user.user_type != 'student':
        messages.error(request, "This page is only accessible to students.")
        return redirect('dashboard')
    
 
    if not hasattr(request.user, 'student'):
        messages.error(request, "Student profile not found. Please contact administrator.")
        return redirect('dashboard')
    
   
    student = request.user.student
    grades = Grade.objects.filter(student=student).select_related('exam__subject', 'exam__exam_type').order_by('-graded_at')
    
    
    grades_by_subject = {}
    for grade in grades:
        if grade.exam and grade.exam.subject:
            subject = grade.exam.subject.name
            if subject not in grades_by_subject:
                grades_by_subject[subject] = []
            grades_by_subject[subject].append(grade)
    
   
    subject_averages = {}
    for subject, subject_grades in grades_by_subject.items():
        if subject_grades:
            
            valid_grades = [grade for grade in subject_grades if hasattr(grade, 'percentage') and grade.percentage is not None]
            if valid_grades:
                avg = sum(grade.percentage for grade in valid_grades) / len(valid_grades)
                subject_averages[subject] = round(avg, 2)
    

    overall_average = sum(subject_averages.values()) / len(subject_averages) if subject_averages else 0
    

    recent_grades = grades[:10]
    
    context = {
        'student': student,
        'grades_by_subject': grades_by_subject,
        'subject_averages': subject_averages,
        'overall_average': round(overall_average, 2),
        'recent_grades': recent_grades,
        'total_grades': grades.count(),
    }
    return render(request, 'grades/my_grades.html', context)

@teacher_or_admin_required
def generate_report_card(request, student_pk):
    """Generate report card for a student"""
    student = get_object_or_404(Student, pk=student_pk)
    
    if request.method == 'POST':
        form = ReportCardForm(request.POST)
        if form.is_valid():
            report_card = form.save(commit=False)
            report_card.generated_by = request.user.teacher if request.user.user_type == 'teacher' else None
            report_card.save()
            
      
            report_card.calculate_grades()
            report_card.calculate_rank()
            
            messages.success(request, f'Report card generated for {student.user.full_name}!')
            return redirect('grades:view_report_card', pk=report_card.pk)
    else:
        form = ReportCardForm(initial={'student': student})
    
    return render(request, 'grades/generate_report_card.html', {'form': form, 'student': student})

@login_required
def view_report_card(request, pk):
    """View a report card"""
    report_card = get_object_or_404(ReportCard.objects.select_related('student__user', 'academic_year'), pk=pk)
    

    if request.user.user_type == 'student' and request.user != report_card.student.user:
        messages.error(request, "You can only view your own report card.")
        return redirect('grades:my_grades')
    
    grades = Grade.objects.filter(
        student=report_card.student,
        exam__academic_year=report_card.academic_year
    ).select_related('exam__subject', 'exam__exam_type').order_by('exam__subject__name')
    
   
    grades_by_subject = {}
    for grade in grades:
        subject = grade.exam.subject.name
        if subject not in grades_by_subject:
            grades_by_subject[subject] = []
        grades_by_subject[subject].append(grade)
    
    context = {
        'report_card': report_card,
        'grades_by_subject': grades_by_subject,
    }
    return render(request, 'grades/view_report_card.html', context)

@admin_required
def exam_types(request):
    """Manage exam types"""
    exam_types = ExamType.objects.all().order_by('name')
    
    context = {
        'exam_types': exam_types,
    }
    return render(request, 'grades/exam_types.html', context)

@admin_required
def add_exam_type(request):
    """Add new exam type"""
    if request.method == 'POST':
        form = ExamTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam type added successfully!')
            return redirect('grades:exam_types')
    else:
        form = ExamTypeForm()
    
    return render(request, 'grades/add_exam_type.html', {'form': form})


@login_required
def get_grade_comments(request):
    """AJAX view to get predefined grade comments"""
    category = request.GET.get('category')
    comments = GradeComment.objects.filter(is_active=True)
    
    if category:
        comments = comments.filter(category=category)
    
    comments_list = list(comments.values('id', 'comment', 'category'))
    return JsonResponse({'comments': comments_list})

@login_required
def grade_statistics(request):
    """AJAX view to get grade statistics"""
    exam_id = request.GET.get('exam_id')
    
    if exam_id:
        exam = get_object_or_404(Exam, id=exam_id)
        grades = Grade.objects.filter(exam=exam)
        
        stats = {
            'total_students': exam.students_count,
            'grades_entered': grades.count(),
            'average_percentage': grades.aggregate(avg=Avg('percentage'))['avg'] or 0,
            'pass_rate': grades.filter(percentage__gte=40).count() / grades.count() * 100 if grades.count() > 0 else 0,
        }
        
      
        distribution = {}
        for grade in grades:
            letter = grade.letter_grade
            distribution[letter] = distribution.get(letter, 0) + 1
        
        return JsonResponse({
            'stats': stats,
            'distribution': distribution
        })
    
    return JsonResponse({'error': 'Invalid exam ID'})
