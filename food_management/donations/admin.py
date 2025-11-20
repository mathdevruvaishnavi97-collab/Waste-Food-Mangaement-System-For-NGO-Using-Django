from django.contrib import admin
from .models import UserProfile, FoodDonation

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(FoodDonation)
class FoodDonationAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'donor', 'food_type', 'quantity', 'expiry_hours', 'status', 'created_at')
    list_filter = ('status', 'food_type', 'created_at')
    search_fields = ('food_name', 'donor__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Food Information', {
            'fields': ('donor', 'food_type', 'food_name', 'quantity', 'expiry_hours', 'description', 'food_image')
        }),
        ('Pickup Details', {
            'fields': ('pickup_location', 'pickup_address', 'pickup_latitude', 'pickup_longitude')
        }),
        ('Status', {
            'fields': ('status', 'accepted_by', 'created_at', 'updated_at')
        }),
    )
