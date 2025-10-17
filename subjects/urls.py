from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.subject_list, name='list'),
    path('<int:pk>/', views.subject_detail, name='detail'),
    path('add/', views.add_subject, name='add'),
    path('<int:pk>/edit/', views.edit_subject, name='edit'),
    path('<int:subject_pk>/assign-teacher/', views.assign_teacher, name='assign_teacher'),
    path('<int:subject_pk>/curriculum/', views.manage_curriculum, name='manage_curriculum'),
    path('<int:subject_pk>/curriculum/add/', views.add_curriculum, name='add_curriculum'),
    
    # AJAX endpoints
    path('api/by-grade/', views.get_subjects_by_grade, name='by_grade'),
]