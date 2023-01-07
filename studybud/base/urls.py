from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import home, room, create_room, update_room, delete_room, login_page, logout_user, register_user, \
    delete_message, user_profile, update_user, topics_page, activity_page, edit_message, reply_message, activate, \
    private_messages, create_chat, chat, update_chat, delete_chat, add_image, add_friend, friends_list, delete_friend, \
    friend_request, private_room, create_private_room, private_rooms_list, update_private_room, priv_room_add_friends, \
    priv_room_delete_friends

# dial_view, create_dialog_viwe, priv_mess_view, dialog

urlpatterns = [
    path('', home, name='home'),

    path('room/<int:pk>', room, name='room'),
    path('create_room', create_room, name='create_room'),
    path('update_room/<int:pk>', update_room, name='update_room'),
    path('delete_room/<int:pk>', delete_room, name='delete_room'),

    path('topics/', topics_page, name='topics_page'),
    path('activity', activity_page, name='activity_page'),

    path('delete_message/<int:pk>', delete_message, name='delete_message'),
    path('edit_message/<int:pk>', edit_message, name='edit_message'),
    path('reply_message/<int:pk>', reply_message, name='reply_message'),
    path('room/<int:pk>/add_image/', add_image, name='add_image_room'),
    path('chat/<int:pk>/add_image/', add_image, name='add_image_chat'),

    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('profile/<int:pk>', user_profile, name='user_profile'),
    path('update_user/', update_user, name='update_user'),

    # path('form/', index, name = 'index'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        activate, name='activate'),
    path('chats/<int:pk>', private_messages, name='private_messages'),
    path('create_chat/<int:pk>', create_chat, name='create_chat'),
    path('chat/<int:pk>', chat, name='chat'),
    path('update_chat/<int:pk>', update_chat, name='update_chat'),
    path('delete_chat/<int:pk>', delete_chat, name='delete_chat'),
    # path('dialogs/<int:pk>', login_required(dialog), name='dialogs'),
    # path('dialogs/create/', login_required(create_dialog_viwe), name='create_dialog'),
    # path('dialogs/<int:chat_id>', login_required(priv_mess_view), name='messages'),
    path('add_friend/<int:pk>', add_friend, name='add_friend'),
    path('delete_friend/<int:pk>', delete_friend, name='delete_friend'),
    path('friends_list/', friends_list, name='friends_list'),
    path('friend_request/<pk>', friend_request, name="friend_request"),

    path('private_room/<int:pk>', private_room, name='private_room'),
    path('create_private_room', create_private_room, name='create_private_room'),
    path('private_rooms_list', private_rooms_list, name='private_rooms_list'),
    path('update_private_room/<int:pk>', update_private_room, name='update_private_room'),
    path('add_friends_private_room/<int:pk>', priv_room_add_friends, name='add_friend_pr_r'),
    path('private_room/<int:rm_pk>/delete_friend/<int:us_pk>', priv_room_delete_friends, name='delete_priv_room'),
    # path('update_private_room/<int:pk>', update_private_room, name='update_private_room'),
    # path('delete_private_room/<int:pk>', delete_private_room, name='delete_private_room'),
]
