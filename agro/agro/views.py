from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def index(request):
    return render(request, 'htmldemo.net/index.html')

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
            return render(request, 'htmldemo.net/registration.html', {'error': 'Please enter a valid email address!'})
        
        if password1 == password2:
            try:
                if User.objects.filter(username=username).exists():
                    return render(request, 'htmldemo.net/registration.html', {'error': 'Username is already taken!'})
                if User.objects.filter(email=email).exists():
                    return render(request, 'htmldemo.net/registration.html', {'error': 'Email is already registered!'})
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                # Do NOT log in the user here
                messages.success(request, "Registration successful! Please log in.")
                return redirect('login')  # Redirect to login page
            except Exception as e:
                return render(request, 'htmldemo.net/registration.html', {'error': str(e)})
        else:
            return render(request, 'htmldemo.net/registration.html', {'error': 'Passwords do not match!'})
    else:
        return render(request, 'htmldemo.net/registration.html')

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