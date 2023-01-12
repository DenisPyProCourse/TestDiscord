from django.db import models

from accounts.models import User


class Friends(models.Model):
    friend = models.ManyToManyField(User, verbose_name="Friend", related_name='friends')
    is_friend = models.BooleanField(default=False)
    host_friend = models.ForeignKey(User,
                                    verbose_name="Host friend",
                                    on_delete=models.CASCADE,
                                    related_name='host_friend',
                                    null=True)

    def __str__(self):
        users = User.objects.filter(friends=self)

        return (lambda x: f'friendship between {next(x)} and {next(x)}')(i.username for i in users)
