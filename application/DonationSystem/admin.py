from django.contrib import admin
from .models import NGO_MedicineListInfo, Donor_MedicineListInfo

# Register your models here.
class NGO_MedicineListInfoAdmin(admin.ModelAdmin):
    list_display = ('NGO', 'MedicineName', 'DosageAmount', 'MedicinePriority', 'AmountRequired')
    
class Donor_MedicineListInfoAdmin(admin.ModelAdmin):
    list_display = ('Donor', 'MedicineName', 'DosageAmount', 'PillsLeft', 'ExpiryDateImage')

admin.site.register(NGO_MedicineListInfo, NGO_MedicineListInfoAdmin)
admin.site.register(Donor_MedicineListInfo, Donor_MedicineListInfoAdmin)
