from django.db import models
from accounts.models import User
from private_message.models import Chat
from private_room.models import Private_Room


class Topic(models.Model):
    name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    from room.models import Room
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
