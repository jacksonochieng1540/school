from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.decorators import admin_required, teacher_or_admin_required
from .models import ClassRoom, Grade, Subject, AcademicYear
from .forms import ClassRoomForm, SubjectForm, GradeForm

@login_required
def class_list(request):
    classes = ClassRoom.objects.select_related('grade', 'class_teacher', 'academic_year').annotate(
        student_count=Count('student')
    )
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        classes = classes.filter(
            Q(name__icontains=search_query) |
            Q(grade__name__icontains=search_query) |
            Q(room_number__icontains=search_query)
        )
    
    # Filter by grade
    grade_filter = request.GET.get('grade')
    if grade_filter:
        classes = classes.filter(grade_id=grade_filter)
    
    # Filter by academic year
    academic_year_filter = request.GET.get('academic_year')
    if academic_year_filter:
        classes = classes.filter(academic_year_id=academic_year_filter)
    
    # Pagination
    paginator = Paginator(classes, 12)
    page_number = request.GET.get('page')
    classes = paginator.get_page(page_number)
    
    context = {
        'classes': classes,
        'grades': Grade.objects.all(),
        'academic_years': AcademicYear.objects.all(),
        'search_query': search_query,
        'grade_filter': grade_filter,
        'academic_year_filter': academic_year_filter,
    }
    return render(request, 'classes/class_list.html', context)

@login_required
def class_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    students = classroom.student_set.filter(is_active=True).select_related('user')
    
    context = {
        'classroom': classroom,
        'students': students,
        'subjects': Subject.objects.filter(grades=classroom.grade),
    }
    return render(request, 'classes/class_detail.html', context)

@admin_required
def add_class(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class added successfully!')
            return redirect('classes:list')
    else:
        form = ClassRoomForm()
    
    return render(request, 'classes/add_class.html', {'form': form})

@admin_required
def edit_class(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('classes:detail', pk=classroom.pk)
    else:
        form = ClassRoomForm(instance=classroom)
    
    return render(request, 'classes/edit_class.html', {'form': form, 'classroom': classroom})

@login_required
def subject_list(request):
    subjects = Subject.objects.prefetch_related('grades')
    
    search_query = request.GET.get('search')
    if search_query:
        subjects = subjects.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
    # Filter by core/elective
    subject_type = request.GET.get('type')
    if subject_type == 'core':
        subjects = subjects.filter(is_core=True)
    elif subject_type == 'elective':
        subjects = subjects.filter(is_core=False)
    
    paginator = Paginator(subjects, 12)
    page_number = request.GET.get('page')
    subjects = paginator.get_page(page_number)
    
    context = {
        'subjects': subjects,
        'search_query': search_query,
        'subject_type': subject_type,
    }
    return render(request, 'subjects/subject_list.html', context)

@admin_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subjects:list')
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/add_subject.html', {'form': form})