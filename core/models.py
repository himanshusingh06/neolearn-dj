# models.py
from django.db import models
from django.contrib.auth.models import User

class UserDefinedCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_courses')
    course_name = models.CharField(max_length=255)
    details = models.TextField()
    resources = models.TextField(blank=True, null=True)  # To store resources from Gemini AI
    created_at = models.DateTimeField(auto_now_add=True)
