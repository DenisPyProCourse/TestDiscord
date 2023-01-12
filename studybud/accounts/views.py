from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.views import PasswordResetView

from friends.models import Friends
from private_message.models import Chat
from private_message.views import create_chat
from .forms import MyUserCreationForm, UserForm, MyPasswordResetForm
from base.models import Topic, Message
from .models import User
from .token import account_activation_token
from .tasks import send_email_verif

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')
    context = {'page': page}
    return render(request, 'accounts/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_email_verif.delay(mail_subject, message, to_email)
            em_conf = True
            return render(request, 'accounts/email_confirmation.html', context={'em_conf': em_conf})
        else:
            messages.error(request, 'An error occurred during registration')
    context = {'form': form}
    return render(request, 'accounts/login_register.html', context)


def activate(request, uidb64, token):
    Userr = User
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Userr.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Userr.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        em_log = True
        return render(request,'accounts/email_confirmation.html', context= {'em_log': em_log})  #'Thank you for your email
        # confirmation. Now you can login your account.'
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk=user.id)
    return render(request, 'accounts/update_user.html', {'form': form})


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_count = rooms.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[0:5]
    chats = Chat.objects.filter(members__in=[request.user.id, user.id]).annotate(
        c=Count('members')).filter(c=2)
    friends = Friends.objects.filter(friend__in=[request.user.id, user.id]).annotate(
        c=Count('friend')).filter(c=2)
    if request.method == 'POST':
        if chats.count() == 0:
            create_chat(pk=pk)
        else:
            chats = chats.first()
    chats = chats.first()
    connection = friends.first()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'room_count': room_count,
        'chats': chats,
        'friends': friends,
        'connection': connection
    }
    return render(request, 'accounts/profile.html', context)


class MyPasswordResetView(PasswordResetView):
    form_class = MyPasswordResetForm
