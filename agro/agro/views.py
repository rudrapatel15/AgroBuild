from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random
from django.core.mail import send_mail

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'htmldemo.net/Registration.html', {'error': 'Please enter a valid email address!'})

        if password1 != password2:
            return render(request, 'htmldemo.net/Registration.html', {'error': 'Passwords do not match!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'htmldemo.net/Registration.html', {'error': 'Username is already taken!'})
        if User.objects.filter(email=email).exists():
            return render(request, 'htmldemo.net/Registration.html', {'error': 'Email is already registered!'})

        # Generate OTP and send email
        otp = random.randint(1000, 9999)
        request.session['pending_user'] = {
            'username': username,
            'email': email,
            'password': password1,
            'otp': str(otp)
        }
        subject = f"Verify Your AgroBuild Account, {username}!"
        message = (
            f"Dear {username},\n\n"
            f"Welcome to AgroBuild! 🌱 Thank you for joining our mission to grow a greener future.\n "
            f"To complete your registration, please use the following One-Time Password (OTP):\n\n"
            f"OTP: {otp}\n\n"
            f"This OTP is valid for 10 minutes. Do not share it with anyone to keep your account secure.\n\n"
            f"With Green Regards,\n"
            f"The AgroBuild Team\n"
            f"AGROBUILD Private Limited\n"
            f"B-42 Akruti Garden, Nehrunagar\n"
            f"Ahmedabad, 380015\n"
            f"📞 8128383925\n"
            f"✉️ shopmulti9859@gmail.com"
        )
        send_mail(
            subject,
            message,
            None,
            [email],
            fail_silently=False,
        )
        return render(request, 'htmldemo.net/otp_verify.html', {'email': email})

    return render(request, 'htmldemo.net/Registration.html')

def otp_verify_view(request):
    if request.method == "POST":
        otp_input = request.POST.get('otp')
        pending_user = request.session.get('pending_user')
        if not pending_user:
            return redirect('registration')
        if otp_input == pending_user['otp']:
            # Create user
            user = User.objects.create_user(
                username=pending_user['username'],
                email=pending_user['email'],
                password=pending_user['password']
            )
            del request.session['pending_user']
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            return render(request, 'htmldemo.net/otp_verify.html', {'email': pending_user['email'], 'error': 'Invalid OTP!'})
    else:
        return redirect('registration')
    
def index(request):
    return render(request, 'htmldemo.net/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'htmldemo.net/login.html', 
                        {'error': 'Please enter a valid email address!'})
        try:
            user = User.objects.get(username=username, email=email)
            authenticated_user = authenticate(username=username, password=password)
            
            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                messages.success(request, "You have successfully logged in!")
                return redirect('index')
            else:
                return render(request, 'htmldemo.net/login.html', 
                            {'error': 'Invalid password!'})
        except User.DoesNotExist:
            return render(request, 'htmldemo.net/login.html', 
                        {'error': 'Username and email combination not found!'})
    else:
        return render(request, 'htmldemo.net/login.html')

def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, "You have successfully logged out!")
        return redirect('index')