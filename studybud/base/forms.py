from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
# from django.http import request

from .models import Room, User, Message, PrivateMessage, Chat, Private_Room, Friends


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

class PrivateRoomForm(ModelForm):
    class Meta:
        model = Private_Room
        fields = '__all__'
        exclude = ['host']



class PrivateRoomFormCreate(PrivateRoomForm):
    # model = Private_Room
    # class Meta()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['host'] = self.instance.host
        self.fields['room_friends'] = forms.MultipleChoiceField(
            choices=[
                (friend.id, f'{friend.username}') for friend in
                # (User.objects.get(username=friend), f'{User.objects.get(username=friend)}') for friend in
                # Friends.objects.filter((Q(is_friend=True) |
                #                     Q(host_friend_id=self.instance.id)))
                User.objects.filter((Q(friends__is_friend=True) &
                                     Q(friends__host_friend_id=self.instance.host.id))) if
                friend.id != self.instance.host.id and friend not in self.instance.room_friends.all()
            ],
            label='room_friends',
            required=False,
        )

    class Meta(PrivateRoomForm.Meta):
        exclude = ['host', 'name', 'description', 'updated', 'created']


# class PrivateRoomAddFriend(PrivateRoomForm):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # self.fields['host'] = request.user
#         self.fields['friends'] = forms.ChoiceField(
#             choices=[
#                 (friend.pk, f'{friend}') for friend in
#                 Friends.objects.all()
#             ],
#             label='friends',
#             required=False,
#         )
#         class Meta:
#             fields = ['friends']

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
        fields = ['body']

class MessgImg(ModelForm):
    class Meta:
        model = Message
        fields = ['images']

class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = '__all__'
        exclude = ['members']

