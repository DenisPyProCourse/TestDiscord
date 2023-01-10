from django.forms import ModelForm

from private_message.models import Chat


class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = '__all__'
        exclude = ['members']
