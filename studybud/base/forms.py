from django.forms import ModelForm

from .models import Message


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class MessgImg(ModelForm):
    class Meta:
        model = Message
        fields = ['images']
