from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from .models import UserProfile, FoodDonation

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type', 'donor')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, user_type=user_type, phone=phone, address=address)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if user_profile.user_type == 'donor':
        my_donations = FoodDonation.objects.filter(donor=request.user)
        pending_count = my_donations.filter(status='pending').count()
        accepted_count = my_donations.filter(status='accepted').count()
        completed_count = my_donations.filter(status='completed').count()
        
        context = {
            'user_profile': user_profile,
            'my_donations': my_donations[:5],
            'total_donations': my_donations.count(),
            'pending_count': pending_count,
            'accepted_count': accepted_count,
            'completed_count': completed_count,
        }
    else:
        available_donations = FoodDonation.objects.filter(status='pending')
        my_accepted = FoodDonation.objects.filter(accepted_by=request.user)
        
        context = {
            'user_profile': user_profile,
            'available_donations': available_donations[:5],
            'my_accepted': my_accepted[:5],
            'total_available': available_donations.count(),
            'total_accepted': my_accepted.count(),
        }
    
    return render(request, 'dashboard.html', context)

@login_required
def post_food(request):
    if request.method == 'POST':
        food_type = request.POST.get('food_type')
        food_name = request.POST.get('food_name')
        quantity = request.POST.get('quantity')
        expiry_hours = request.POST.get('expiry_hours')
        description = request.POST.get('description')
        pickup_location = request.POST.get('pickup_location')
        pickup_address = request.POST.get('pickup_address')
        food_image = request.FILES.get('food_image')
        
        donation = FoodDonation.objects.create(
            donor=request.user,
            food_type=food_type,
            food_name=food_name,
            quantity=quantity,
            expiry_hours=expiry_hours,
            description=description,
            pickup_location=pickup_location,
            pickup_address=pickup_address,
            food_image=food_image
        )
        
        messages.success(request, 'Food donation posted successfully!')
        return redirect('dashboard')
    
    return render(request, 'post_food.html')

@login_required
def food_history(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if user_profile.user_type == 'donor':
        donations = FoodDonation.objects.filter(donor=request.user)
    else:
        donations = FoodDonation.objects.filter(accepted_by=request.user)
    
    status_filter = request.GET.get('status')
    if status_filter:
        donations = donations.filter(status=status_filter)
    
    context = {
        'donations': donations,
        'user_profile': user_profile,
    }
    return render(request, 'food_history.html', context)

@login_required
def profile(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        user_profile.phone = request.POST.get('phone', '')
        user_profile.address = request.POST.get('address', '')
        
        if request.FILES.get('profile_image'):
            user_profile.profile_image = request.FILES.get('profile_image')
        
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'profile.html', context)

@login_required
def available_donations(request):
    donations = FoodDonation.objects.filter(status='pending').exclude(donor=request.user)
    
    food_type = request.GET.get('food_type')
    if food_type:
        donations = donations.filter(food_type=food_type)
    
    search = request.GET.get('search')
    if search:
        donations = donations.filter(
            Q(food_name__icontains=search) | 
            Q(description__icontains=search) |
            Q(pickup_location__icontains=search)
        )
    
    context = {
        'donations': donations,
    }
    return render(request, 'available_donations.html', context)

@login_required
@transaction.atomic
def accept_donation(request, donation_id):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if user_profile.user_type != 'ngo':
        messages.error(request, 'Only NGOs can accept donations.')
        return redirect('dashboard')
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('available_donations')
    
    donation = get_object_or_404(FoodDonation.objects.select_for_update(), id=donation_id)
    
    if donation.status == 'pending':
        donation.status = 'accepted'
        donation.accepted_by = request.user
        donation.save()
        messages.success(request, f'You have accepted the donation: {donation.food_name}')
    else:
        messages.error(request, 'This donation is no longer available.')
    
    return redirect('available_donations')

@login_required
def update_donation_status(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id)
    
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if user_profile.user_type == 'donor' and donation.donor == request.user:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['picked_up', 'completed', 'cancelled']:
                donation.status = new_status
                donation.save()
                messages.success(request, f'Donation status updated to {new_status}')
    elif donation.accepted_by == request.user:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['picked_up', 'completed']:
                donation.status = new_status
                donation.save()
                messages.success(request, f'Donation status updated to {new_status}')
    
    return redirect('food_history')

@login_required
def donation_detail(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id)
    context = {
        'donation': donation,
    }
    return render(request, 'donation_detail.html', context)
