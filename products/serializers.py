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
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    variants = ProductVariantSerializer(many=True)
    images = ProductImageSerializer(many=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'old_price', 'image', 'is_active',
            'category', 'variants', 'images',
            'created_at'
        ]

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'old_price', 'image', 'category', 'is_active']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None