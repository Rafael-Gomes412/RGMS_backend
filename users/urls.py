from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Profil
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Adresses
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='address-set-default'),
]