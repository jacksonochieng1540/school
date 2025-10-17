from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    # Grades
    path('', views.grade_list, name='list'),
    path('my-grades/', views.my_grades, name='my_grades'),
    path('add/', views.add_grade, name='add'), 
    # Exams
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/', views.exam_list, name='exams'),
    path('exams/create/', views.create_exam, name='create_exam'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:exam_pk>/enter-grades/', views.enter_grades, name='enter_grades'),
    
    # Report Cards
    path('report-card/<int:student_pk>/generate/', views.generate_report_card, name='generate_report_card'),
    path('report-card/<int:pk>/', views.view_report_card, name='view_report_card'),
    
    # Exam Types
    path('exam-types/', views.exam_types, name='exam_types'),
    path('exam-types/add/', views.add_exam_type, name='add_exam_type'),
    
    # AJAX endpoints
    path('api/comments/', views.get_grade_comments, name='grade_comments'),
    path('api/statistics/', views.grade_statistics, name='grade_statistics'),
]