"""
Forms for CRPify Authentication Module.
Provides robust server-side validation, password hashing, and user creation.
"""

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator

UserModel = get_user_model()


class LoginForm(forms.Form):
    """
    Form for user login supporting either email or username with 'Remember Me'.
    """
    username = forms.CharField(
        label="Email or Username",
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email or username',
            'autocomplete': 'username',
            'id': 'id_login_username',
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'id': 'id_login_password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label="Remember me for 14 days",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember_me',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username.strip(),
                password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid email/username or password. Please double-check your credentials.",
                    code='invalid_login',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    "This account is currently inactive. Please contact support.",
                    code='inactive',
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class SignupForm(forms.Form):
    """
    Form for user registration.
    Validates full name, email uniqueness, username format and uniqueness,
    password strength, password confirmation, and terms acceptance.
    """
    username_validator = UnicodeUsernameValidator()

    full_name = forms.CharField(
        label="Full Name",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Alex Morgan',
            'autocomplete': 'name',
            'id': 'id_full_name',
        })
    )
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@company.com',
            'autocomplete': 'email',
            'id': 'id_email',
        })
    )
    username = forms.CharField(
        label="Username",
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'autocomplete': 'username',
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        help_text="Must contain at least 8 characters, and not be entirely numeric or commonly used.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a secure password',
            'autocomplete': 'new-password',
            'id': 'id_signup_password',
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
            'id': 'id_confirm_password',
        })
    )
    terms = forms.BooleanField(
        required=True,
        label="I agree to the Terms of Service and Privacy Policy",
        error_messages={
            'required': 'You must accept the Terms of Service and Privacy Policy to create an account.'
        },
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_terms',
        })
    )

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name) < 2:
            raise forms.ValidationError("Please provide your full name (at least 2 characters).")
        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists. Please sign in instead.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        self.username_validator(username)
        if UserModel.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match. Please verify and try again.")
            else:
                # Validate password strength with Django's configured password validators
                temp_user = UserModel(username=username or '', email=email or '')
                try:
                    validate_password(password, user=temp_user)
                except ValidationError as error:
                    for err in error.error_list:
                        self.add_error('password', err)

        return cleaned_data

    def save(self):
        """
        Creates and returns the new User instance with hashed password.
        Splits full_name into first_name and last_name.
        """
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = UserModel.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        return user
