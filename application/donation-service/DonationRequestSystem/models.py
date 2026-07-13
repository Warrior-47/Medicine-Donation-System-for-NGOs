from django.db import models

# Create your models here.
class donationRequest(models.Model):
    # User ids live in user-service; names/phone are denormalized at
    # request-creation time because services don't share tables.
    Donor_id = models.BigIntegerField(db_index=True)
    Donor_name = models.CharField(max_length=100, blank=True)
    Donor_phone = models.CharField(max_length=11, blank=True)
    NGO_id = models.BigIntegerField(db_index=True)
    NGO_name = models.CharField(max_length=100, blank=True)
    Delivery_type = models.CharField(max_length=11,blank=True)
    Pick_Up_address = models.CharField(max_length=150,blank=True)
    Acceptance_Status = models.BooleanField(default=False)
    Pick_Up_date = models.DateField(null=True,blank=True,default=None)
    Pick_Up_time = models.TimeField(null=True,blank=True,default=None)
    Delivery_status = models.CharField(max_length=20,default='pending')


    def __str__(self):
        return f'{self.Donor_name,self.NGO_name}'

class donatedMedicines(models.Model):
    donation_request = models.ForeignKey(donationRequest, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100,blank=True)
    dosage_amount = models.IntegerField()
    number_of_pills = models.IntegerField()

    def __str__(self):
        return f'{self.medicine_name}'
