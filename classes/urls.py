from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list, name='list'),
    path('<int:pk>/', views.class_detail, name='detail'),
    path('add/', views.add_class, name='add'),
    path('<int:pk>/edit/', views.edit_class, name='edit'),
]