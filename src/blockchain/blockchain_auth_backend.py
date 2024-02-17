from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class BlockchainAuthBackend(BaseBackend):
    def authenticate(self, request, address=None):
        try:
            user = User.objects.get(username=address)
            return user
        except User.DoesNotExists:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None