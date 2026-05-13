from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def user_type_required(allowed_types):
  
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type not in allowed_types:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
 
    return user_type_required(['admin'])(view_func)

def teacher_or_admin_required(view_func):
  
    return user_type_required(['admin', 'teacher'])(view_func)

def student_required(view_func):
 
    return user_type_required(['student'])(view_func)

def parent_required(view_func):
  
    return user_type_required(['parent'])(view_func)
