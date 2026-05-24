from django.db import models
from django.contrib.auth.models import User

class Permit(models.Model):
    title = models.CharField(max_length=255)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permits')
    description = models.TextField()
    status = models.CharField(max_length=50, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
