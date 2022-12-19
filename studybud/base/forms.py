from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User, Message, PrivateMessage, Chat


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    # def clean(self):
    #     """
    #     Validate password_1 and password_2 values
    #     """
    #     if 'password_1' in self.cleaned_data and 'password_2' in self.cleaned_data:
    #         if self.cleaned_data['password_1'] != self.cleaned_data['password_2']:
    #             e = forms.ValidationError('You must type the same password each time.')
    #             self._errors['password_2'] = e.messages
    #             raise e
    #     return self.cleaned_data

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio', 'lnkdn']

    def clean_lnkdn(self):
        lnkdn = self.cleaned_data['lnkdn']
        if lnkdn is not None and 'linkedin' not in lnkdn:
            raise ValidationError('Not a LinkedIn link', code='invalid')
            # self.add_error("lnkdn", "asdasdasdasd")

        return lnkdn

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body', 'images']

class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = '__all__'
        exclude = ['members']

