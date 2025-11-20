from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPES = (
        ('donor', 'Donor'),
        ('ngo', 'NGO'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='donor')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class FoodDonation(models.Model):
    FOOD_TYPES = (
        ('cooked', 'Cooked Food'),
        ('raw', 'Raw Food'),
        ('packaged', 'Packaged Food'),
        ('fruits', 'Fruits & Vegetables'),
        ('bakery', 'Bakery Items'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    food_type = models.CharField(max_length=20, choices=FOOD_TYPES)
    food_name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    expiry_hours = models.IntegerField(help_text='Hours until food expires')
    description = models.TextField()
    food_image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    
    pickup_location = models.CharField(max_length=500)
    pickup_address = models.TextField()
    pickup_latitude = models.FloatField(blank=True, null=True)
    pickup_longitude = models.FloatField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_donations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.food_name} by {self.donor.username}"
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def is_expired(self):
        expiry_time = self.created_at + timezone.timedelta(hours=self.expiry_hours)
        return timezone.now() > expiry_time
    
    @property
    def time_remaining(self):
        expiry_time = self.created_at + timezone.timedelta(hours=self.expiry_hours)
        remaining = expiry_time - timezone.now()
        if remaining.total_seconds() <= 0:
            return "Expired"
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
