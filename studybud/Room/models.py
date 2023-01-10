from django.db import models

from base.models import User, Topic


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250, null=True, blank=True)  # null for DB, blank for Forms
    participants = models.ManyToManyField(User, related_name='participants', blank=True)  # we have User model already,
    # and need to add related name which will be not the same
    updated = models.DateTimeField(auto_now=True)  # auto_now update time after every update
    created = models.DateTimeField(auto_now_add=True)  # auto_now_add make the time only once after creation

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
