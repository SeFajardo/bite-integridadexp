from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list_create, name='report-list-create'),
    path('stats/', views.report_stats, name='report-stats'),
    path('<int:pk>/', views.report_detail, name='report-detail'),
    path('<int:pk>/verify/', views.report_verify, name='report-verify'),
]
