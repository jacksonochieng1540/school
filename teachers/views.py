from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from accounts.decorators import admin_required, teacher_or_admin_required
from .models import Teacher, TeacherSchedule, TeacherLeave
from .forms import TeacherForm, TeacherLeaveForm, TeacherScheduleForm
from classes.models import Subject

@login_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').prefetch_related('subjects').filter(is_active=True)
    

    search_query = request.GET.get('search')
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
   
    subject_filter = request.GET.get('subject')
    if subject_filter:
        teachers = teachers.filter(subjects__id=subject_filter)
    
    
    qualification_filter = request.GET.get('qualification')
    if qualification_filter:
        teachers = teachers.filter(qualification=qualification_filter)
    
    employment_filter = request.GET.get('employment_status')
    if employment_filter:
        teachers = teachers.filter(employment_status=employment_filter)
   
    sort_by = request.GET.get('sort', 'user__first_name')
    if sort_by in ['user__first_name', 'user__last_name', 'employee_id', 'joining_date', 'experience_years']:
        teachers = teachers.order_by(sort_by)
    
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)
    
    context = {
        'teachers': teachers,
        'subjects': Subject.objects.all(),
        'qualifications': Teacher.QUALIFICATION_CHOICES,
        'employment_statuses': Teacher.EMPLOYMENT_STATUS_CHOICES,
        'search_query': search_query,
        'subject_filter': subject_filter,
        'qualification_filter': qualification_filter,
        'employment_filter': employment_filter,
        'sort_by': sort_by,
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
    }
    return render(request, 'teachers/teacher_list.html', context)

@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(
        Teacher.objects.select_related('user').prefetch_related('subjects', 'schedules'),
        pk=pk
    )
    
   
    assigned_classes = teacher.assigned_classes.select_related('grade', 'academic_year')
    
    
    recent_leaves = teacher.leave_requests.all()[:5]
    
    schedules = teacher.schedules.select_related('subject', 'class_room').order_by('day_of_week', 'start_time')
    
   
    schedule_by_day = {}
    for schedule in schedules:
        day = schedule.get_day_of_week_display()
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(schedule)
    
    context = {
        'teacher': teacher,
        'assigned_classes': assigned_classes,
        'recent_leaves': recent_leaves,
        'schedule_by_day': schedule_by_day,
        'can_edit': request.user.user_type == 'admin' or request.user == teacher.user,
    }
    return render(request, 'teachers/teacher_detail.html', context)

@admin_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher {teacher.full_name} added successfully!')
            return redirect('teachers:detail', pk=teacher.pk)
    else:
        form = TeacherForm()
    
    return render(request, 'teachers/add_teacher.html', {'form': form})

@admin_required
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f'Teacher {teacher.full_name} updated successfully!')
            return redirect('teachers:detail', pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    
    return render(request, 'teachers/edit_teacher.html', {'form': form, 'teacher': teacher})

@login_required
def teacher_schedule(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
   
    if request.user.user_type not in ['admin'] and request.user != teacher.user:
        messages.error(request, "You don't have permission to view this schedule.")
        return redirect('teachers:list')
    
    schedules = teacher.schedules.select_related('subject', 'class_room').order_by('day_of_week', 'start_time')
    
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    schedule_grid = {}
    
    for day in days:
        schedule_grid[day] = schedules.filter(day_of_week=day)
    
    context = {
        'teacher': teacher,
        'schedule_grid': schedule_grid,
        'can_edit': request.user.user_type == 'admin',
    }
    return render(request, 'teachers/teacher_schedule.html', context)

@admin_required
def add_schedule(request, teacher_pk):
    teacher = get_object_or_404(Teacher, pk=teacher_pk)
    
    if request.method == 'POST':
        form = TeacherScheduleForm(request.POST, teacher=teacher)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.teacher = teacher
            schedule.save()
            messages.success(request, 'Schedule added successfully!')
            return redirect('teachers:schedule', pk=teacher.pk)
    else:
        form = TeacherScheduleForm(teacher=teacher)
    
    return render(request, 'teachers/add_schedule.html', {'form': form, 'teacher': teacher})

@login_required
def request_leave(request, pk=None):
    if pk:
        teacher = get_object_or_404(Teacher, pk=pk)
   
        if request.user.user_type != 'admin' and request.user != teacher.user:
            messages.error(request, "You don't have permission to request leave for this teacher.")
            return redirect('teachers:list')
    else:
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            messages.error(request, "Only teachers can request leave.")
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherLeaveForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.teacher = teacher
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('teachers:detail', pk=teacher.pk)
    else:
        form = TeacherLeaveForm()
    
    return render(request, 'teachers/request_leave.html', {'form': form, 'teacher': teacher})

@admin_required
def manage_leaves(request):
    leaves = TeacherLeave.objects.select_related('teacher__user', 'approved_by').order_by('-applied_on')
    

    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    paginator = Paginator(leaves, 20)
    page_number = request.GET.get('page')
    leaves = paginator.get_page(page_number)
    
    context = {
        'leaves': leaves,
        'status_filter': status_filter,
        'status_choices': TeacherLeave.STATUS_CHOICES,
    }
    return render(request, 'teachers/manage_leaves.html', context)

@admin_required
def approve_leave(request, leave_pk):
    leave_request = get_object_or_404(TeacherLeave, pk=leave_pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_comments = request.POST.get('admin_comments', '')
        
        if action == 'approve':
            leave_request.status = 'approved'
            leave_request.approved_by = request.user
            leave_request.approved_on = timezone.now()
            leave_request.admin_comments = admin_comments
            leave_request.save()
            messages.success(request, f'Leave request for {leave_request.teacher.full_name} approved.')
        
        elif action == 'reject':
            leave_request.status = 'rejected'
            leave_request.approved_by = request.user
            leave_request.approved_on = timezone.now()
            leave_request.admin_comments = admin_comments
            leave_request.save()
            messages.success(request, f'Leave request for {leave_request.teacher.full_name} rejected.')
        
        return redirect('teachers:manage_leaves')
    
    return render(request, 'teachers/approve_leave.html', {'leave_request': leave_request})


@login_required
def get_teachers_by_subject(request):
    """AJAX view to get teachers by subject"""
    subject_id = request.GET.get('subject_id')
    if subject_id:
        teachers = Teacher.objects.filter(
            subjects__id=subject_id, 
            is_active=True
        ).select_related('user').values('id', 'user__first_name', 'user__last_name', 'employee_id')
        
        return JsonResponse({
            'teachers': list(teachers)
        })
    return JsonResponse({'teachers': []})

@admin_required
def bulk_import_teachers(request):
    """Bulk import teachers from CSV file"""
    if request.method == 'POST':
        messages.info(request, 'Bulk import functionality coming soon!')
        return redirect('teachers:list')
    
    return render(request, 'teachers/bulk_import.html')
