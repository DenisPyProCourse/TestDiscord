from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('api/', include('base.api.urls')),
    path('friends/', include('Friends.urls')),
    path('private_message/', include('private_message.urls')),
    path('room/', include('Room.urls')),
    path('private_rooms/', include('PrivateRoom.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)