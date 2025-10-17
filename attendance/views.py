from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.decorators import teacher_or_admin_required
from django.utils import timezone
from students.models import Student
from teachers.models import Teacher
from classes.models import ClassRoom, Subject
from .models import AttendanceRecord, AttendanceSummary
from .forms import BulkAttendanceForm, AttendanceSearchForm, AttendanceReportForm,AttendanceForm


@login_required
def attendance_list(request):
    """List and filter attendance records"""
    records = AttendanceRecord.objects.select_related(
        'student__user', 'class_room', 'subject', 'teacher__user'
    )

    # User-based filtering
    if request.user.user_type == 'teacher':
        records = records.filter(teacher__user=request.user)
    elif request.user.user_type == 'student':
        records = records.filter(student__user=request.user)

    # Apply search filters
    form = AttendanceSearchForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['date_from']:
            records = records.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            records = records.filter(date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['class_room']:
            records = records.filter(class_room=form.cleaned_data['class_room'])
        if form.cleaned_data['subject']:
            records = records.filter(subject=form.cleaned_data['subject'])
        if form.cleaned_data['status']:
            records = records.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['student_search']:
            search = form.cleaned_data['student_search']
            records = records.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__student_id__icontains=search)
            )

    records = records.order_by('-date', 'student__user__first_name')

    paginator = Paginator(records, 25)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)

    context = {
        'records': records,
        'form': form,
        'total_records': AttendanceRecord.objects.count(),
    }
    return render(request, 'attendance/attendance_list.html', context)

@teacher_or_admin_required
def mark_attendance(request):
    """Mark attendance for individual students"""
    
    # Get initial filter parameters
    class_room_id = request.GET.get('class_room')
    subject_id = request.GET.get('subject')
    date = request.GET.get('date', timezone.now().date())
    
    class_room = None
    subject = None
    students = Student.objects.none()
    
    if class_room_id:
        class_room = get_object_or_404(ClassRoom, id=class_room_id)
        students = Student.objects.filter(class_room=class_room, is_active=True)
    
    if subject_id:
        subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        # Remove the form validation since we're processing manually
        saved_count = 0
        
        for student in students:
            status_key = f'status_{student.id}'
            remarks_key = f'remarks_{student.id}'
            
            # Get data directly from request.POST instead of form.cleaned_data
            status = request.POST.get(status_key)
            remarks = request.POST.get(remarks_key, '')
            
            if status:
                # Get or create attendance record
                attendance, created = AttendanceRecord.objects.get_or_create(
                    student=student,
                    class_room=class_room,
                    subject=subject,
                    date=date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user.teacher if hasattr(request.user, 'teacher') else None,
                    }
                )
                
                if not created:
                    # Update existing record
                    attendance.status = status
                    attendance.remarks = remarks
                    attendance.marked_by = request.user.teacher if hasattr(request.user, 'teacher') else None
                    attendance.save()
                
                saved_count += 1
        
        messages.success(request, f'Attendance marked for {saved_count} students!')
        return redirect('attendance:list')
    
    # Get existing attendance records for the selected date
    existing_attendance = {}
    if class_room and date:
        attendance_records = AttendanceRecord.objects.filter(
            class_room=class_room,
            date=date,
            subject=subject
        )
        existing_attendance = {record.student_id: record for record in attendance_records}
    
    # Get available classes and subjects
    class_rooms = ClassRoom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'class_room': class_room,
        'subject': subject,
        'students': students,
        'class_rooms': class_rooms,
        'subjects': subjects,
        'date': date,
        'existing_attendance': existing_attendance,
    }
    
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def bulk_mark_attendance(request, class_room_id, subject_id=None):
    """Mark attendance for all students in a given class (and subject if provided)"""
    class_room = get_object_or_404(ClassRoom, pk=class_room_id)
    subject = get_object_or_404(Subject, pk=subject_id) if subject_id else None

    # Get students in this class
    students = Student.objects.filter(
        class_room=class_room,
        is_active=True
    ).select_related('user').order_by('user__first_name', 'user__last_name')

    # Get today's existing attendance
    existing_attendance = {}
    records = AttendanceRecord.objects.filter(
        class_room=class_room,
        subject=subject,
        date=timezone.now().date()
    )
    for record in records:
        existing_attendance[record.student_id] = record

    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST, students=students, existing_attendance=existing_attendance)
        if form.is_valid():
            saved_count = 0
            for student in students:
                status = form.cleaned_data.get(f'status_{student.id}')
                remarks = form.cleaned_data.get(f'remarks_{student.id}', '')

                record, created = AttendanceRecord.objects.update_or_create(
                    student=student,
                    class_room=class_room,
                    subject=subject,
                    date=timezone.now().date(),
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'teacher': Teacher.objects.get(user=request.user) if request.user.user_type == 'teacher' else None,
                    }
                )

                # Update summary
                update_attendance_summary(student, record.date)
                saved_count += 1

            messages.success(request, f"Attendance marked for {saved_count} students.")
            return redirect('attendance:list')
    else:
        form = BulkAttendanceForm(students=students, existing_attendance=existing_attendance)

    context = {
        'form': form,
        'students': students,
        'class_room': class_room,
        'subject': subject,
    }
    return render(request, 'attendance/bulk_mark_attendance.html', context)


@login_required
def my_attendance(request):
    """Student view of their own attendance"""
    if request.user.user_type != 'student':
        messages.error(request, "This page is only accessible to students.")
        return redirect('dashboard')

    # Safe check for student relationship
    if not hasattr(request.user, 'student'):
        messages.error(request, "Student profile not found. Please contact administrator.")
        return redirect('dashboard')

    student = request.user.student
    records = AttendanceRecord.objects.filter(student=student).select_related(
        'subject', 'class_room', 'teacher__user'
    ).order_by('-date')

    current_year = timezone.now().year
    summaries = AttendanceSummary.objects.filter(student=student, year=current_year).order_by('-month')

    context = {
        'student': student,
        'records': records[:10],  # recent records
        'summaries': summaries,
        'total_records': records.count(),
    }
    return render(request, 'attendance/my_attendance.html', context)

@login_required
def attendance_reports(request):
    """Generate attendance reports"""
    if request.method == 'POST':
        form = AttendanceReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            class_room = form.cleaned_data['class_room']
            students = form.cleaned_data['students']

            records = AttendanceRecord.objects.filter(date__range=(date_from, date_to))
            if class_room:
                records = records.filter(class_room=class_room)
            if students.exists():
                records = records.filter(student__in=students)

            context = {
                'form': form,
                'records': records,
                'report_type': report_type,
            }
            return render(request, f'attendance/reports/{report_type}_report.html', context)
    else:
        form = AttendanceReportForm()

    return render(request, 'attendance/attendance_reports.html', {'form': form})


# --- Helpers ---
def update_attendance_summary(student, date):
    """Recalculate attendance summary for a student for the given month"""
    month, year = date.month, date.year
    records = AttendanceRecord.objects.filter(
        student=student, date__year=year, date__month=month
    )

    summary, created = AttendanceSummary.objects.get_or_create(
        student=student, month=month, year=year,
        defaults={'total_days': 0, 'present_days': 0, 'absent_days': 0, 'late_days': 0}
    )

    summary.total_days = records.count()
    summary.present_days = records.filter(status='present').count()
    summary.absent_days = records.filter(status='absent').count()
    summary.late_days = records.filter(status='late').count()
    summary.save()
