from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductVariantSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_id', 'quantity', 'unit_price', 'total']
        read_only_fields = ['unit_price']

    def get_total(self, obj):
        return obj.get_total()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'items',
            'full_name', 'street', 'city', 'postal_code', 'country',
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'total_price', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0

        for item_data in items_data:
            variant_id = item_data.pop('variant_id')
            from products.models import ProductVariant
            variant = ProductVariant.objects.get(id=variant_id)

            # Vérifie le stock
            if variant.stock < item_data['quantity']:
                order.delete()
                raise serializers.ValidationError(
                    f"Stock insuffisant pour {variant.product.name} - {variant.size.name}"
                )

            unit_price = variant.product.price
            OrderItem.objects.create(
                order=order,
                variant=variant,
                unit_price=unit_price,
                **item_data
            )

            # Déduit le stock
            variant.stock -= item_data['quantity']
            variant.save()

            total += unit_price * item_data['quantity']

        order.total_price = total
        order.save()
        return order


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'city', 'created_at']