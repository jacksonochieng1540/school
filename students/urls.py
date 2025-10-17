from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('add/', views.add_student, name='add'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_student, name='edit'),
    path('<int:pk>/grades/', views.student_grades, name='grades'),
    path('<int:pk>/attendance/', views.student_attendance, name='attendance'),
    path('<int:pk>/upload-document/', views.upload_document, name='upload_document'),
    path('bulk-import/', views.bulk_import, name='bulk_import'),
    
    # AJAX endpoints
    path('api/by-class/', views.get_students_by_class, name='by_class'),
]