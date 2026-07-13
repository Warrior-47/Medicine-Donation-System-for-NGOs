from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class NGO_MedicineListInfo(models.Model):
    MedicineName = models.CharField(max_length=100, blank=False)
    DosageAmount = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    MedicinePriority = models.PositiveIntegerField(validators=[MaxValueValidator(3)],blank=False)
    AmountRequired = models.PositiveIntegerField(validators=[MinValueValidator(1)],blank=False)
    # User id in user-service; services don't share foreign keys.
    NGO_id = models.BigIntegerField(db_index=True)

    def __str__(self) -> str:
        return f"NGO | {self.MedicineName} Priority: {self.MedicinePriority}"

class Donor_MedicineListInfo(models.Model):
    MedicineName = models.CharField(max_length=100, blank=False)
    DosageAmount = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    PillsLeft = models.IntegerField(validators=[MinValueValidator(0)],blank=False)
    ExpiryDateImage = models.ImageField(upload_to='medicine_images')

    # User id in user-service; services don't share foreign keys.
    Donor_id = models.BigIntegerField(db_index=True)

    def __str__(self) -> str:
        return f"Donor | {self.MedicineName} Dosage: {self.DosageAmount}"
