from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from payapp.models import Currency
from django.db import transaction
from django.http import JsonResponse


@csrf_protect
def signup_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            currency_type = form.cleaned_data.get('currency_type')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please try a different username.")
                return render(request, "signup.html", {"form": form})
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, "signup.html", {"form": form})
            if password1 != password2:
                messages.error(request, "Passwords did not match!")
                return render(request, "signup.html", {"form": form})

            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password1)
                Currency.objects.create(user=user, currency_type=currency_type)

            login(request, user)
            messages.success(request, f'Welcome, {username}, your account has been registered successfully!')
            return redirect('home')
        else:
            messages.warning(request, "Unsuccessful registration. Please try again.")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


@csrf_protect
def signin_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password, )
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'signin.html', {"form": form})


@csrf_protect
def logout_user(request):
    logout(request)
    messages.info(request, "Logged Out!")
    return redirect('home')


def home(request):
    return render(request, "home.html")

