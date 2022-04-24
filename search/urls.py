from django.urls import path
from . import views

urlpatterns = [
    path('ngo_search/<str:ngo_name>/', views.ngo_search, name='ngo_search'),
    path('priority_search/<str:search_type>/', views.priority_search, name='priority_search'),
    path('show_ngo_list/<int:pk>/', views.show_ngo_list, name='show_ngo_list'),
]