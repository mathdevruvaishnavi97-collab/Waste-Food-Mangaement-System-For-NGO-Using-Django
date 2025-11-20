from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
  path('dashboard/', views.dashboard, name='dashboard'),

    path('post-food/', views.post_food, name='post_food'),
    path('food-history/', views.food_history, name='food_history'),
    path('profile/', views.profile, name='profile'),
    path('available-donations/', views.available_donations, name='available_donations'),
    path('accept-donation/<int:donation_id>/', views.accept_donation, name='accept_donation'),
    path('update-status/<int:donation_id>/', views.update_donation_status, name='update_donation_status'),
    path('donation/<int:donation_id>/', views.donation_detail, name='donation_detail'),
]
