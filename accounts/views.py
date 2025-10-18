from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ProfileUpdateForm
from django.utils import timezone

class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    
    context = {
        'today': timezone.now().date(),
    }
    

    if request.user.user_type == 'admin':
        from students.models import Student
        from teachers.models import Teacher
        from classes.models import ClassRoom, Subject
        
        context.update({
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_classes': ClassRoom.objects.count(),
            'total_subjects': Subject.objects.count(),
        })
    
    elif request.user.user_type == 'teacher':
        if hasattr(request.user, 'teacher'):
            teacher = request.user.teacher
            context.update({
                'my_classes_count': teacher.assigned_classes.count() if hasattr(teacher, 'assigned_classes') else 0,
                'my_subjects_count': teacher.subjects.count() if hasattr(teacher, 'subjects') else 0,
                'my_students_count': getattr(teacher, 'total_students', 0),
            })
        else:
            context.update({
                'my_classes_count': 0,
                'my_subjects_count': 0,
                'my_students_count': 0,
            })
    
    elif request.user.user_type == 'student':
        if hasattr(request.user, 'student'):
            student = request.user.student
            context.update({
                'my_class': student.class_room,
                'recent_average': 0,  
                'total_subjects': 0,
                'attendance_rate': getattr(student, 'attendance_percentage', 0),
            })
        else:
            context.update({
                'my_class': None,
                'recent_average': 0,
                'total_subjects': 0,
                'attendance_rate': 0,
            })
    
    context['recent_attendance'] = []
    
    return render(request, 'dashboard.html', context)
