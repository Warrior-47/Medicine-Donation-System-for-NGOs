from django.urls import path

from . import api

urlpatterns = [
    path('users/<int:pk>/', api.user_detail, name='api_user_detail'),
    path('users/', api.user_list, name='api_user_list'),
    path('ngos/', api.ngo_list, name='api_ngo_list'),
]
