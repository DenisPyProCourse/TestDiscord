from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('api/', include('room.api.urls')),
    path('friends/', include('friends.urls')),
    path('private_message/', include('private_message.urls')),
    path('room/', include('room.urls')),
    path('private_rooms/', include('private_room.urls')),
    path('accounts/', include('accounts.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)