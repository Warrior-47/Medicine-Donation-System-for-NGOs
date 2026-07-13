from django.urls import path

from . import api

urlpatterns = [
    path('donor/<int:user_id>/', api.donor_medicines, name='api_donor_medicines'),
    path('ngo/<int:user_id>/', api.ngo_medicines, name='api_ngo_medicines'),
    path('ngo/', api.all_ngo_medicines, name='api_all_ngo_medicines'),
]
