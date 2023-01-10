from django.urls import path
from .views import private_messages, create_chat, chat, update_chat, delete_chat


urlpatterns = [
    path('<int:pk>', private_messages, name='private_messages'),
    path('create_chat/<int:pk>', create_chat, name='create_chat'),
    path('chat/<int:pk>', chat, name='chat'),
    path('update_chat/<int:pk>', update_chat, name='update_chat'),
    path('delete_chat/<int:pk>', delete_chat, name='delete_chat'),
]
