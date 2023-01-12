from django.db import models

from accounts.models import User


class Private_Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250, null=True, blank=True)
    room_friends = models.ManyToManyField(User, related_name='room_friends', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
