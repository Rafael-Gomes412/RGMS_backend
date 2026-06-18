import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = request.data.get('amount')
            order_id = request.data.get('order_id')

            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),  # Stripe utilise les centimes
                currency='eur',
                metadata={
                    'order_id': order_id,
                    'user_id': request.user.id,
                }
            )

            return Response({
                'client_secret': intent.client_secret
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'confirmed'
            order.save()
            return Response({'message': 'Commande confirmée !'})
        except Order.DoesNotExist:
            return Response(
                {'error': 'Commande introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )