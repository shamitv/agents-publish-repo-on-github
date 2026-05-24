from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/login', views.api_login, name='api_login'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/permits', views.permit_list, name='permit_list'),
    path('api/permits/<int:permit_id>', views.permit_detail, name='permit_detail'),
    path('api/permits/<int:permit_id>/upload', views.upload_document, name='upload_document'),
    path('api/permits/<int:permit_id>/approve', views.approve_permit, name='approve_permit'),
]
