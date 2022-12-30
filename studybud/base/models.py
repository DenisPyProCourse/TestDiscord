from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import naturaltime
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
            # then for some users there may not be any information about the visit, we will return information that the last visit is unknown
        return _('Unknown')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250, null=True, blank=True) # null for DB, blank for Forms
    participants = models.ManyToManyField(User, related_name='participants', blank=True) # we have User model already, and need to add related name which will be not the same
    updated = models.DateTimeField(auto_now=True) # auto_now update time after every update
    created = models.DateTimeField(auto_now_add=True) # auto_now_add make the time only once after creation

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name



class Chat(models.Model):

    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, verbose_name=_("Member"), related_name='members')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    # # @models.permalink
    # def get_absolute_url(self):
    #     return reverse('users:messages', (), {'chat_id': self.pk})

# class Message(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE) # One to Many relationship, mes - child, room - father
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True) # Cascade means that if we delete parent(room) - child will dead
#     body = models.TextField() # user should to input smthng here
#     updated = models.DateTimeField(auto_now=True)
#     created = models.DateTimeField(auto_now_add=True)
#     # on_click = models.BooleanField(default=False)
#     reply = models.IntegerField(blank=True, null=True)
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
#     images = models.ImageField(null=True, upload_to='mess_img/')
#     private_room = models.ForeignKey(Private_Room, on_delete=models.CASCADE, null=True)
#
#     class Meta:
#         ordering = ['-updated', '-created']
#
#     def __str__(self):
#         return self.body[0:50] # representation view must not be so large


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

class Friends(models.Model):
    friend = models.ManyToManyField(User, verbose_name=_("Friend"), related_name='friends')
    is_friend = models.BooleanField(default=False)
    host_friend = models.ForeignKey(User,
                                    verbose_name=_("Host friend"),
                                    on_delete=models.CASCADE,
                                    related_name='host_friend',
                                    null=True)

    def __str__(self):
        users = User.objects.filter(friends=self)
        for i in users:
            if i != self.host_friend:
                return i.username


class Private_Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250, null=True, blank=True) # null for DB, blank for Forms
    # participants = models.ManyToManyField(User, related_name='participants', blank=True) # we have User model already, and need to add related name which will be not the same
    updated = models.DateTimeField(auto_now=True) # auto_now update time after every update
    created = models.DateTimeField(auto_now_add=True) # auto_now_add make the time only once after creation
    friends = models.ManyToManyField(Friends, related_name='friends', blank=True)

    # def get_friends(self):
    #     friends = Friends.objects.filter(friends=self)
    #     for i in friends:
    #         if i != self.host:
    #             return i.username

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # One to Many relationship, mes - child, room - father
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True) # Cascade means that if we delete parent(room) - child will dead
    body = models.TextField() # user should to input smthng here
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # on_click = models.BooleanField(default=False)
    reply = models.IntegerField(blank=True, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    images = models.ImageField(null=True, upload_to='mess_img/')
    private_room = models.ForeignKey(Private_Room, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] # representation view must not be so large