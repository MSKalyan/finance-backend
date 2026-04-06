from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin')
    )

    email = models.EmailField(unique=True)  

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'     
    REQUIRED_FIELDS = []          