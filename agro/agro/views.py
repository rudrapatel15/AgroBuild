from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth

def index(request):
    return render(request, 'htmldemo.net/index.html')

def login_view(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect('index')
        else:
            return render(request, 'htmldemo.net/login.html', {'error': 'Username or password is incorrect!'})
    else:
        return render(request, 'htmldemo.net/login.html')

def register_view(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username=request.POST['username'])
                return render(request, 'htmldemo.net/registration.html', {'error': 'Username is already taken!'})
            except User.DoesNotExist:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                auth.login(request, user)
                messages.success(request, "Registration successful!")
                return redirect('index')
        else:
            return render(request, 'htmldemo.net/registration.html', {'error': 'Passwords do not match!'})
    else:
        return render(request, 'htmldemo.net/registration.html')

def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, "You have successfully logged out!")
        return redirect('index')