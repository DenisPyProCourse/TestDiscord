from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, default='', blank=True)
    lnkdn = models.CharField(max_length=150, null=True, blank=True)

    avatar = models.ImageField(null=True, default='avatar.svg')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250, null=True, blank = True) # null for DB, blank for Forms
    participants = models.ManyToManyField(User, related_name='participants', blank=True) # we have User model already, and need to add related name which will be not the same
    updated = models.DateTimeField(auto_now=True) # auto_now update time after every update
    created = models.DateTimeField(auto_now_add=True) # auto_now_add make the time only once after creation

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Chat(models.Model):
    # DIALOG = 'D'
    # CHAT = 'C'
    # CHAT_TYPE_CHOICES = (
    #     (DIALOG, _('Dialog')),
    #     (CHAT, _('Chat'))
    # )
    #
    # type = models.CharField(
    #     _('Тип'),
    #     max_length=1,
    #     choices=CHAT_TYPE_CHOICES,
    #     default=DIALOG
    # )
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, verbose_name=_("Member"), related_name='members')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # # @models.permalink
    # def get_absolute_url(self):
    #     return reverse('users:messages', (), {'chat_id': self.pk})

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # One to Many relationship, mes - child, room - father
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True) # Cascade means that if we delete parent(room) - child will dead
    body = models.TextField() # user should to input smthng here
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # on_click = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    images = models.ImageField(null=True, upload_to='mess_img/')
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] # representation view must not be so large


class PrivateMessage(models.Model):
    chat = models.ForeignKey(Chat, verbose_name=_("Чат"), on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.CASCADE)
    message = models.TextField(_("Сообщение"))
    pub_date = models.DateTimeField(_('Дата сообщения'), default=timezone.now)
    is_readed = models.BooleanField(_('Прочитано'), default=False)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message