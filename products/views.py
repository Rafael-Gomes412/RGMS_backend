from rest_framework import generics, filters
from .models import Category, Product
from rest_framework.permissions import AllowAny
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer


# Liste toutes les catégories
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# Liste tous les produits avec filtres et recherche
class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filtre par catégorie
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filtre par prix
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


# Détail d'un produit via son slug
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('variants__size')