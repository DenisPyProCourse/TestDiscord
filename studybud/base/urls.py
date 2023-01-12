from django.urls import path

from .views import home, delete_message, topics_page, activity_page, edit_message, reply_message, add_image

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
]
