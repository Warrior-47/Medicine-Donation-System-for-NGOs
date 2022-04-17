from django.db import models

from account.models import CustomUser

# Create your models here.
class donationRequest(models.Model):
    Donor_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    NGO_id = models.CharField(max_length=10, blank=True)
    Medicine_list = models.CharField(max_length=11, blank=True)
    Delivery_type = models.CharField(max_length=11,blank=True)
    Pick_Up_address = models.CharField(max_length=150,blank=True)
    Acceptance_Status = models.BooleanField(default=False)
    Pick_Up_date = models.DateField()
    Pick_Up_time = models.TimeField()
    Delivery_status = models.CharField(max_length=20,default='pending')


    def __str__(self):
        return f'{self.Donor_id,self.NGO_id}'