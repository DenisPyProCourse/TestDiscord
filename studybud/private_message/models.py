from django.db import models

from base.models import User


class Chat(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, verbose_name="Member", related_name='members')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


# class private_message(models.Model):
#     chat = models.ForeignKey(Chat, verbose_name=_("Чат"), on_delete=models.CASCADE)
#     author = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.CASCADE)
#     message = models.TextField(_("Сообщение"))
#     pub_date = models.DateTimeField(_('Дата сообщения'), default=timezone.now)
#     is_readed = models.BooleanField(_('Прочитано'), default=False)
#
#     class Meta:
#         ordering = ['pub_date']
#
#     def __str__(self):
#         return self.message
