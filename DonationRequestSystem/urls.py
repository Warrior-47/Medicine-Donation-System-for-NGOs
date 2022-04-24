from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('donation_request/<int:pk>/', views.donation, name='donation'),
    path('test',views.test,name='test')
   
]