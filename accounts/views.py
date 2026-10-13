"""
Views for Sweat Sense Authentication Module.
Handles login, registration, logout, and authenticated redirects.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .forms import LoginForm, SignupForm


def login_view(request):
    """
    Handles user login.
    Redirects already authenticated users to the dashboard.
    Supports login via username or email, and dynamic session duration ('Remember Me').
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    redirect_to = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Handle 'Remember Me'
            remember_me = form.cleaned_data.get('remember_me')
            if remember_me:
                # Persistent session: 14 days (1,209,600 seconds)
                request.session.set_expiry(1209600)
            else:
                # Ephemeral session: expires upon browser close
                request.session.set_expiry(0)

            user_display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"Welcome back, {user_display_name}! You are now signed in.")

            # Validate redirect URL for security (prevent open redirect attacks)
            if redirect_to and url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(redirect_to)

            return redirect('dashboard:home')
        else:
            # Form is invalid - errors will be displayed in the template
            messages.error(request, "Sign-in failed. Please check the credentials provided below.")
    else:
        form = LoginForm(request=request)

    context = {
        'form': form,
        'next': redirect_to,
        'page_title': 'Sign In — Sweat Sense',
    }
    return render(request, 'accounts/login.html', context)


def signup_view(request):
    """
    Handles user registration.
    Redirects already authenticated users to the dashboard.
    Validates all fields, hashes password, and redirects to login upon success.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Welcome aboard, {user.first_name or user.username}! Your account has been created successfully. Please sign in below."
            )
            return redirect('accounts:login')
        else:
            messages.error(
                request,
                "Unable to create account. Please review the highlighted issues below."
            )
    else:
        form = SignupForm()

    context = {
        'form': form,
        'page_title': 'Join Sweat Sense — Biomedical Research',
    }
    return render(request, 'accounts/signup.html', context)


@require_POST
def logout_view(request):
    """
    Handles secure logout via POST request only.
    Invalidates session and redirects to login page.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been successfully signed out of Sweat Sense.")
    return redirect('accounts:login')
