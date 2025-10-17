from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('mark/', views.mark_attendance, name='mark'),  # ADD THIS LINE
    path('bulk/<int:class_room_id>/', views.bulk_mark_attendance, name='bulk_mark'),
    path('bulk/<int:class_room_id>/<int:subject_id>/', views.bulk_mark_attendance, name='bulk_mark_subject'),
    path('my/', views.my_attendance, name='my_attendance'),
    path('reports/', views.attendance_reports, name='reports'),
]