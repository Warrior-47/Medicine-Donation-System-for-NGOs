from django.urls import path
from . import views

urlpatterns = [
    path('medicine/', views.medicine, name='medicine_priority'),
    path('distance/', views.distance, name='distance_priority'),
    path('ngo_search/<str:ngo_name>/', views.ngo_search, name='ngo_search'),
]