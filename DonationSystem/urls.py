from django.urls import path


from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('edit-list/', views.edit_list, name='edit-list'),
    path('add-medicine/', views.add_medicine, name='add-medicine'),
    path('update-medicine/<int:pk>/', views.update_medicine, name='update-medicine'),
    path('delete-medicine/<int:pk>/', views.delete_medicine, name='delete-medicine'),
]