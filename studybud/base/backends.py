from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .models import User
from django.utils import timezone


class MyBackend(ModelBackend):

    def get_user(self, user_id):
        # user.backend = 'django.contrib.auth.backends.ModelBackend'
        try:
            user = User.objects.get(pk=user_id)
            # user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.last_online = timezone.now()  # At the request of the user, we will update the date and time of the last visit
            user.save(update_fields=['last_online'])
            return user
        except User.DoesNotExist:
            return None