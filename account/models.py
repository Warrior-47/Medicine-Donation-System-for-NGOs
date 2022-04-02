from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=100, blank=True)
    identity = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=11, blank=True)

    is_ngo = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.username}, NGO: {self.is_ngo}'