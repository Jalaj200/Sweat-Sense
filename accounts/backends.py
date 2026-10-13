"""
Custom Authentication Backend for Sweat Sense.
Allows users to sign in using either their username or email address.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate against settings.AUTH_USER_MODEL using either username or email.
    Uses case-insensitive matching for both username and email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if not username or not password:
            return None

        # Look up user by case-insensitive username or email
        try:
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by('id').first()
        except Exception:
            return None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
