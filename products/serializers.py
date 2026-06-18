from rest_framework import serializers
from .models import Category, Product, Size, ProductVariant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer()

    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'stock']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    variants = ProductVariantSerializer(many=True)
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'image', 'is_active',
            'category', 'variants', 'images',
            'created_at'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price','old_price', 'image', 'category', 'is_active']