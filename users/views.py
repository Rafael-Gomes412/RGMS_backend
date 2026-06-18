from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Address
from .serializers import RegisterSerializer, UserProfileSerializer, AddressSerializer


# Inscription
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# Profil utilisateur connecté
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# Liste et création d'adresses
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Détail, modification et suppression d'une adresse
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# Définir une adresse par défaut
class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Retire le défaut de toutes les adresses
        Address.objects.filter(user=request.user).update(is_default=False)
        # Met cette adresse en défaut
        address = Address.objects.get(pk=pk, user=request.user)
        address.is_default = True
        address.save()
        return Response({'message': 'Adresse par défaut mise à jour.'}, status=status.HTTP_200_OK)