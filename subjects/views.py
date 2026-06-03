from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from accounts.decorators import admin_required, teacher_or_admin_required
from classes.models import Subject
from .models import SubjectTeacherAssignment, Curriculum
from .forms import SubjectForm, SubjectTeacherAssignmentForm, CurriculumForm

@login_required
def subject_list(request):
    subjects = Subject.objects.prefetch_related('grades', 'teachers')
    
    
    search_query = request.GET.get('search')
    if search_query:
        subjects = subjects.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    subject_type = request.GET.get('type')
    if subject_type == 'core':
        subjects = subjects.filter(is_core=True)
    elif subject_type == 'elective':
        subjects = subjects.filter(is_core=False)
    
    grade_filter = request.GET.get('grade')
    if grade_filter:
        subjects = subjects.filter(grades__id=grade_filter)
    
    subjects = subjects.annotate(
        teacher_count=Count('teachers', distinct=True),
        grade_count=Count('grades', distinct=True)
    )
    
    
    paginator = Paginator(subjects, 12)
    page_number = request.GET.get('page')
    subjects = paginator.get_page(page_number)
    
    from classes.models import Grade
    context = {
        'subjects': subjects,
        'grades': Grade.objects.all(),
        'search_query': search_query,
        'subject_type': subject_type,
        'grade_filter': grade_filter,
    }
    return render(request, 'subjects/subject_list.html', context)

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject.objects.prefetch_related('grades', 'teachers'), pk=pk)
    
    assignments = SubjectTeacherAssignment.objects.filter(
        subject=subject, is_active=True
    ).select_related('teacher__user', 'class_room', 'academic_year')
    
    curriculums = Curriculum.objects.filter(subject=subject).select_related('grade', 'academic_year')
    
    context = {
        'subject': subject,
        'assignments': assignments,
        'curriculums': curriculums,
        'can_edit': request.user.user_type == 'admin',
    }
    return render(request, 'subjects/subject_detail.html', context)

@admin_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" added successfully!')
            return redirect('subjects:detail', pk=subject.pk)
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/add_subject.html', {'form': form})

@admin_required
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('subjects:detail', pk=subject.pk)
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/edit_subject.html', {'form': form, 'subject': subject})

@admin_required
def assign_teacher(request, subject_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    
    if request.method == 'POST':
        form = SubjectTeacherAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, f'Teacher assigned to {subject.name} successfully!')
            return redirect('subjects:detail', pk=subject.pk)
    else:
        form = SubjectTeacherAssignmentForm(initial={'subject': subject})
        form.fields['class_room'].queryset = form.fields['class_room'].queryset.filter(
            grade__in=subject.grades.all()
        )
    
    return render(request, 'subjects/assign_teacher.html', {'form': form, 'subject': subject})

@admin_required
def manage_curriculum(request, subject_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    curriculums = Curriculum.objects.filter(subject=subject).select_related('grade', 'academic_year')
    
    context = {
        'subject': subject,
        'curriculums': curriculums,
    }
    return render(request, 'subjects/manage_curriculum.html', context)

@admin_required
def add_curriculum(request, subject_pk):
    subject = get_object_or_404(Subject, pk=subject_pk)
    
    if request.method == 'POST':
        form = CurriculumForm(request.POST)
        if form.is_valid():
            curriculum = form.save()
            messages.success(request, f'Curriculum for {subject.name} added successfully!')
            return redirect('subjects:manage_curriculum', subject_pk=subject.pk)
    else:
        form = CurriculumForm(initial={'subject': subject})
        form.fields['grade'].queryset = subject.grades.all()
    
    return render(request, 'subjects/add_curriculum.html', {'form': form, 'subject': subject})

@login_required
def get_subjects_by_grade(request):
    """AJAX view to get subjects by grade"""
    grade_id = request.GET.get('grade_id')
    if grade_id:
        subjects = Subject.objects.filter(grades__id=grade_id).values('id', 'name', 'code')
        return JsonResponse({'subjects': list(subjects)})
    return JsonResponse({'subjects': []})
