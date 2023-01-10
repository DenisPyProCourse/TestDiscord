from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.managers import CustomUserManager


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(unique=True, max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, default='', blank=True)
    lnkdn = models.CharField(max_length=150, null=True, blank=True)

    avatar = models.ImageField(null=True, default='avatar.svg')
    last_online = models.DateTimeField(blank=True, null=True)

    # In this method, check that the date of the last visit is not older than 15 minutes
    def is_online(self):
        if self.last_online:
            return (timezone.now() - self.last_online) < timezone.timedelta(minutes=15)
        return False

    # If the user visited the site no more than 15 minutes ago,
    def get_online_info(self):
        if self.is_online():
            # then we return information that he is online
            return _('Online')
        if self.last_online:
            # otherwise we write a message about the last visit
            return _('Last visit {}').format(naturaltime(self.last_online))
            # If you have only recently added information about a user visiting the site
            # then for some users there may not be any information about the visit, we will return information that
            # the last visit is unknown
        return _('Unknown')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    from private_message.models import Chat
    from PrivateRoom.models import Private_Room
    from Room.models import Room
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # One to Many relationship, mes - child, room - father
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)  # Cascade means that if we delete parent(room)-
    # child will dead
    body = models.TextField()  # user should to input smthng here
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    reply = models.IntegerField(blank=True, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    images = models.ImageField(null=True, upload_to='mess_img/')
    private_room = models.ForeignKey(Private_Room, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]  # representation view must not be so large
