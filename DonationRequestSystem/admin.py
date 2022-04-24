from django.contrib import admin

from .models import donationRequest, donatedMedicines
# Register your models here.
class donationRequestAdmin(admin.ModelAdmin):
    list_display = ('Donor', 'NGO', 'Delivery_type', 'Pick_Up_address')

class donatedMedicinesAdmin(admin.ModelAdmin):
    list_display = ('medicine_name','dosage_amount','number_of_pills')


admin.site.register(donationRequest, donationRequestAdmin)
admin.site.register(donatedMedicines,donatedMedicinesAdmin)