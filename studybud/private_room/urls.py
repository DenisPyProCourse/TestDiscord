from django.urls import path
from .views import private_room, create_private_room, private_rooms_list, update_private_room, priv_room_add_friends, \
    priv_room_delete_friends, delete_private_room


urlpatterns = [
    path('private_room/<int:pk>', private_room, name='private_room'),
    path('create_private_room', create_private_room, name='create_private_room'),
    path('', private_rooms_list, name='private_rooms_list'),
    path('update_private_room/<int:pk>', update_private_room, name='update_private_room'),
    path('delete_private_room/<int:pk>', delete_private_room, name='delete_private_room'),
    path('add_friends_private_room/<int:pk>', priv_room_add_friends, name='add_friend_pr_r'),
    path('private_room/<int:rm_pk>/delete_friend/<int:us_pk>', priv_room_delete_friends, name='delete_priv_room'),
]
