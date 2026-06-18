from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['unit_price', 'get_total']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'city', 'created_at']
    list_filter = ['status', 'country']
    search_fields = ['user__email', 'full_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'variant', 'quantity', 'unit_price']
    search_fields = ['order__id', 'variant__product__name']