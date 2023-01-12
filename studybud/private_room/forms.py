from django import forms
from django.db.models import Q
from django.forms import ModelForm

from .models import Private_Room
from accounts.models import User


class PrivateRoomForm(ModelForm):
    class Meta:
        model = Private_Room
        fields = '__all__'
        exclude = ['host']


class PrivateRoomFormCreate(PrivateRoomForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_friends'] = forms.MultipleChoiceField(
            choices=[
                (friend.id, f'{friend.username}') for friend in
                User.objects.filter((Q(friends__is_friend=True) &
                                     Q(friends__friend__id=self.instance.host.id))) if
                friend.id != self.instance.host.id and friend not in self.instance.room_friends.all()
            ],
            label='room_friends',
            required=False,
        )

    class Meta(PrivateRoomForm.Meta):
        exclude = ['host', 'name', 'description', 'updated', 'created']
