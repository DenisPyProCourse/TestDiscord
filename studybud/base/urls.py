from django.urls import path
from .views import home, login_page, logout_user, register_user, delete_message, user_profile, update_user, \
    topics_page, activity_page, edit_message, reply_message, activate, add_image

urlpatterns = [
    path('', home, name='home'),

    path('topics/', topics_page, name='topics_page'),
    path('activity', activity_page, name='activity_page'),

    path('delete_message/<int:pk>', delete_message, name='delete_message'),
    path('edit_message/<int:pk>', edit_message, name='edit_message'),
    path('reply_message/<int:pk>', reply_message, name='reply_message'),
    path('room/<int:pk>/add_image/', add_image, name='add_image_room'),
    path('chat/<int:pk>/add_image/', add_image, name='add_image_chat'),
    path('private_room/<int:pk>/add_image/', add_image, name='add_image_private_room'),

    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('profile/<int:pk>', user_profile, name='user_profile'),
    path('update_user/', update_user, name='update_user'),

    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        activate, name='activate'),
]
