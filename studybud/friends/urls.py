from django.urls import path
from .views import add_friend, friends_list, delete_friend, friend_request


urlpatterns = [
    path('add_friend/<int:pk>', add_friend, name='add_friend'),
    path('delete_friend/<int:pk>', delete_friend, name='delete_friend'),
    path('friends_list/', friends_list, name='friends_list'),
    path('friend_request/<pk>', friend_request, name="friend_request"),
]
