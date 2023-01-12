from django.urls import path
from .views import room, create_room, update_room, delete_room


urlpatterns = [
    path('<int:pk>', room, name='room'),
    path('create_room', create_room, name='create_room'),
    path('update_room/<int:pk>', update_room, name='update_room'),
    path('delete_room/<int:pk>', delete_room, name='delete_room'),
]
