import stripe
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Address
from .models import Order
from .serializers import OrderListSerializer, OrderSerializer

# Initialisation de Stripe avec ta clé secrète backend
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'ta_cle_secrete_ici')


# ==========================================
# VUES EXISTANTES (LISTE, DÉTAIL, ANNULATION)
# ==========================================

# Liste et création de commandes classique
class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderSerializer
        return OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Récupère l'adresse par défaut si pas d'adresse fournie
        user = self.request.user
        address = Address.objects.filter(user=user, is_default=True).first()

        if address and not self.request.data.get('street'):
            serializer.save(
                user=user,
                full_name=address.full_name,
                street=address.street,
                city=address.city,
                postal_code=address.postal_code,
                country=address.country,
            )
        else:
            serializer.save(user=user)


# Détail d'une commande
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Annuler une commande
class OrderCancelView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def patch(self, request, pk):
        order = self.get_queryset().filter(pk=pk).first()

        if not order:
            return Response({'error': 'Commande introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Cette commande ne peut plus être annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remet le stock des produits
        for item in order.items.all():
            item.variant.stock += item.quantity
            item.variant.save()

        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Commande annulée avec succès.'}, status=status.HTTP_200_OK)


# ==========================================
# NOUVELLES VUES D'OPTIMISATION DU PAIEMENT STRIPE
# ==========================================

# 1. Crée la commande ET génère le PaymentIntent Stripe au clic sur "Payer"
class CheckoutSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        
        address_data = data.get('address', {})
        items_data = data.get('items', [])
        total_amount = data.get('total_amount') # Reçu sous forme de string/float : "45.99"

        if not items_data or not address_data:
            return Response({'message': 'Données de livraison ou panier manquantes.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Conversion du montant total en centimes pour Stripe (Ex: 45.99 -> 4599)
            amount_in_cents = int(float(total_amount) * 100)

            # Création de la commande en base de données avec les données transmises
            serializer = OrderSerializer(data={
                'full_name': address_data.get('full_name'),
                'street': address_data.get('street'),
                'city': address_data.get('city'),
                'postal_code': address_data.get('postal_code'),
                'country': address_data.get('country', 'France'),
                'items': items_data
            })
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Sauvegarde de la commande associée à l'user, statut initialisé à 'pending'
            order = serializer.save(user=user, status='pending')

            # Demande de création du jeton de paiement sécurisé à Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='eur',
                metadata={
                    'order_id': order.id,
                    'user_email': user.email
                }
            )

            # On renvoie les deux éléments indispensables pour le front-end React
            return Response({
                'order_id': order.id,
                'client_secret': intent.client_secret
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Erreur critique lors du Checkout Stripe :", str(e))
            return Response({'message': 'Erreur serveur lors de l\'initialisation du paiement.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 2. Confirme le statut payé de la commande une fois Stripe validé côté Front
class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Le paiement Stripe a réussi, on passe le statut de la commande à 'confirmed'
            order.status = 'confirmed'
            order.save()
            
            return Response({'message': 'Commande confirmée et payée avec succès.'}, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({'message': 'Commande introuvable ou n\'appartient pas à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)