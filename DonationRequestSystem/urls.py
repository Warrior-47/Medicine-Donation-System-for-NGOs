from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('donation_request/<int:pk>/', views.donation, name='donation'),
    path('test',views.test,name='test'),
    path('ngo_notification/',views.donation_decision,name='ngo_notification'),
    path('donation_details/<int:pk>/',views.donationDetails,name='donationDetails'),
    path('dashboard/<int:pk>/',views.donationDetailsInPerson,name='donationDetailsIP'),
    path('dashboard/<int:pk>/',views.donationReject,name='donationReject'),
    
    
   
]