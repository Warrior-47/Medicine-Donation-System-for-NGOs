"""Internal JSON API exposing user data to the other services."""

from django.http import JsonResponse

from common.internal_api import require_internal_token
from .models import CustomUser


def _serialize(user):
    return {
        'id': user.id,
        'username': user.username,
        'fullname': user.fullname,
        'email': user.email,
        'phone': user.phone,
        'is_ngo': user.is_ngo,
    }


@require_internal_token
def user_detail(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return JsonResponse({'detail': 'user not found'}, status=404)
    return JsonResponse(_serialize(user))


@require_internal_token
def user_list(request):
    """Bulk lookup: /api/users/?ids=1,2,3"""
    ids_param = request.GET.get('ids', '')
    ids = [int(part) for part in ids_param.split(',') if part.strip().isdigit()]
    users = CustomUser.objects.filter(id__in=ids)
    return JsonResponse({'users': [_serialize(u) for u in users]})


@require_internal_token
def ngo_list(request):
    """NGO search: /api/ngos/?name=<substring> (empty name returns all NGOs)."""
    name = request.GET.get('name', '')
    ngos = CustomUser.objects.filter(is_ngo=True)
    if name:
        ngos = ngos.filter(fullname__icontains=name)
    return JsonResponse({'ngos': [_serialize(u) for u in ngos]})
