from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [

    path('', views.teacher_list, name='list'),
    path('add/', views.add_teacher, name='add'),
    path('<int:pk>/', views.teacher_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_teacher, name='edit'),
    

    path('<int:pk>/schedule/', views.teacher_schedule, name='schedule'),
    path('<int:teacher_pk>/schedule/add/', views.add_schedule, name='add_schedule'),
    

    path('leave/request/', views.request_leave, name='request_leave'),
    path('<int:pk>/leave/request/', views.request_leave, name='request_leave_for'),
    path('leaves/', views.manage_leaves, name='manage_leaves'),
    path('leaves/<int:leave_pk>/approve/', views.approve_leave, name='approve_leave'),
    
    path('bulk-import/', views.bulk_import_teachers, name='bulk_import'),
 
    path('api/by-subject/', views.get_teachers_by_subject, name='by_subject'),
]
