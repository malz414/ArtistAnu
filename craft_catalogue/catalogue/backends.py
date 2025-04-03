# catalogue/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrUsernameAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                return None
                
        if user.check_password(password):
            return user
        return None
    
class CaseInsensitiveModelBackend(ModelBackend):
    """
    Custom authentication backend that ensures case-insensitive username login.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Convert username to lowercase to perform case-insensitive login
        try:
            user = get_user_model().objects.get(username=username.lower())
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None