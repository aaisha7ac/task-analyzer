from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('tasks/analyze/', views.analyze_tasks, name='analyze'),
    path('tasks/suggest/', views.suggest_tasks, name='suggest'),
]