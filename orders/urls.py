from django.urls import path
from . import views

urlpatterns = [
    # Gestion des commandes classique
    path('', views.OrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    
    # Nouvelle logique de paiement optimisée (Liée au nouveau Checkout.jsx)
    path('checkout-submit/', views.CheckoutSubmitView.as_view(), name='checkout-submit'),
    path('confirm/', views.OrderConfirmView.as_view(), name='order-confirm'),
]