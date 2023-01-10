from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from base.models import User, Message


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio', 'lnkdn']

    def clean_lnkdn(self):
        lnkdn = self.cleaned_data['lnkdn']
        if lnkdn is not None and 'linkedin' not in lnkdn:
            raise ValidationError('Not a LinkedIn link', code='invalid')
        return lnkdn


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class MessgImg(ModelForm):
    class Meta:
        model = Message
        fields = ['images']
