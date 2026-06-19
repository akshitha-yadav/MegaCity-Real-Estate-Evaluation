from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


# ---------------- HOME ----------------
def index(request):
    return render(request, "index.html")


# ---------------- LOGIN ----------------
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/user/userhome/')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


# ---------------- REGISTER ----------------
def user_registration(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/register/')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully")
        return redirect('/login/')

    return render(request, "register.html")


# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    return redirect('/login/')