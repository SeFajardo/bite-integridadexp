from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.alert_list, name='alert-list'),
    path('alerts/<int:pk>/', views.alert_detail, name='alert-detail'),
    path('alerts/<int:pk>/resolve/', views.alert_resolve, name='alert-resolve'),
    path('dashboard/', views.audit_dashboard, name='audit-dashboard'),
]
