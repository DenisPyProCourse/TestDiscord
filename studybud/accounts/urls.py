from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path
from .views import login_page, logout_user, register_user, user_profile, update_user, activate, MyPasswordResetView

urlpatterns = [
    path('update_user/', update_user, name='update_user'),
    path('profile/<int:pk>', user_profile, name='user_profile'),

    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         activate, name='activate'),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", PasswordChangeDoneView.as_view(), name="password_change_done",),
    path("password_reset/", MyPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done",),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm",),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete",),
]
