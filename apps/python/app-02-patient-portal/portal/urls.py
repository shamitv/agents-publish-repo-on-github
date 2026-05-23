from django.urls import path
from portal import views

urlpatterns = [
    path('', views.serve_index, name='index'),
    path('api/auth/login', views.login_view, name='login'),
    path('api/auth/logout', views.logout_view, name='logout'),
    path('api/auth/me', views.get_me, name='me'),
    path('api/patients/search', views.search_patients, name='search_patients'),
    path('api/patients/<int:patient_id>/records', views.get_patient_records, name='patient_records'),
    path('api/appointments', views.list_appointments, name='list_appointments'),
    path('api/appointments/new', views.create_appointment, name='create_appointment'),
]
