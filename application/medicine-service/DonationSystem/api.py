"""Internal JSON API exposing medicine lists to the other services."""

from django.http import JsonResponse

from common.internal_api import require_internal_token
from .models import Donor_MedicineListInfo, NGO_MedicineListInfo


@require_internal_token
def donor_medicines(request, user_id):
    medicines = list(
        Donor_MedicineListInfo.objects.filter(Donor_id=user_id)
        .order_by('id')
        .values('id', 'MedicineName', 'DosageAmount', 'PillsLeft')
    )
    return JsonResponse({'medicines': medicines})


@require_internal_token
def ngo_medicines(request, user_id):
    medicines = list(
        NGO_MedicineListInfo.objects.filter(NGO_id=user_id)
        .order_by('id')
        .values('id', 'MedicineName', 'DosageAmount', 'MedicinePriority', 'AmountRequired')
    )
    return JsonResponse({'medicines': medicines})


@require_internal_token
def all_ngo_medicines(request):
    """Every NGO medicine entry, grouped-friendly ordering (for priority search)."""
    medicines = list(
        NGO_MedicineListInfo.objects.order_by('NGO_id', 'id')
        .values('NGO_id', 'MedicineName', 'MedicinePriority')
    )
    return JsonResponse({'medicines': medicines})
