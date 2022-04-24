from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('donation_request/<int:pk>/', views.donation, name='donation'),
    path('ngo_notification/',views.donation_decision,name='ngo_notification'),
    path('donation_details/<int:pk>/',views.donationDetails,name='donationDetails'),
    path('accept/<int:pk>/',views.donationDetailsInPerson,name='donationDetailsIP'),
    path('reject/<int:pk>/',views.donationReject,name='donationReject'),
    path('complete/<int:pk>/',views.donationComplete,name='donationComplete'),
    
    
   
]