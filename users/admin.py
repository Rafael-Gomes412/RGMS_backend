from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'phone', 'is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username']
    list_filter = ['is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Infos supplémentaires', {'fields': ('phone', 'avatar')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'postal_code', 'country', 'is_default']
    search_fields = ['full_name', 'city']
    list_filter = ['country', 'is_default']