from email.policy import default
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class NGO_MedicineListInfo(models.Model):
    MedicineName = models.CharField(max_length=100, blank=False)
    DosageAmount = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    MedicinePriority = models.PositiveIntegerField(validators=[MaxValueValidator(3)],blank=False)
    AmountRequired = models.PositiveIntegerField(validators=[MinValueValidator(1)],blank=False)
    NGO = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"NGO | {self.MedicineName} Priority: {self.MedicinePriority}"

class Donor_MedicineListInfo(models.Model):
    MedicineName = models.CharField(max_length=100, blank=False)
    DosageAmount = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    PillsLeft = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    ExpiryDateImage = models.ImageField(upload_to='medicine_images')

    Donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Donor | {self.MedicineName} Dosage: {self.DosageAmount}"

