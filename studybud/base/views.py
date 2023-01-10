from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from Friends.models import Friends
from private_message.models import Chat
from private_message.views import create_chat
from PrivateRoom.models import Private_Room
from Room.models import Room
from base.forms import MyUserCreationForm, MessgImg, UserForm, MessageForm
from base.models import User, Topic, Message
from base.token import account_activation_token


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
    return render(request, 'base/login_register.html', context)


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
            message = render_to_string('base/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            em_conf = True
            return render(request, 'base/email_confirmation.html', context={'em_conf': em_conf})
        else:
            messages.error(request, 'An error occurred during registration')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)


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
        return render(request,'base/email_confirmation.html', context= {'em_log': em_log})  #'Thank you for your email
        # confirmation. Now you can login your account.'
    else:
        return HttpResponse('Activation link is invalid!')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__first_name__icontains=q)
    ).order_by('-updated')
    topics = Topic.objects.all().order_by('-updated')[0:10]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:7]
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)


def add_image(request, pk):
    room, chat, priv_room = None, None, None
    img = MessgImg()
    if 'private_room' in request.path:
        priv_room = Private_Room.objects.get(id=pk)
        if request.method == 'POST':
            img = MessgImg(request.POST, request.FILES, instance=Message.objects.create(
                user=request.user,
                body='',
                private_room=priv_room
            ))
            if img.is_valid():
                img.save()
                return redirect('private_room', priv_room.id)
    elif 'room' in request.path:
        room = Room.objects.get(id=pk)
        if request.method == 'POST':
            img = MessgImg(request.POST, request.FILES, instance=Message.objects.create(
                user=request.user,
                body='',
                room=room
            ))
            if img.is_valid():
                img.save()
                return redirect('room', room.id)
    else:
        chat = Chat.objects.get(id=pk)
        if request.method == 'POST':
            img = MessgImg(request.POST, request.FILES, instance=Message.objects.create(
                user=request.user,
                body='',
                chat=chat
            ))
            if img.is_valid():
                img.save()
                return redirect('chat', chat.id)
    context = {
        'img': img,
        'room': room,
        'chat': chat,
        'priv_room': priv_room
    }
    return render(request, 'base/add_image.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    """
    After the end of project I can try to make a func with Celery to delete Topics & Rooms with 0 rooms
    :param request:
    :param pk:
    :return:
    """
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowe here!!!')
    if request.method == 'POST':
        message.delete()
        if message.room:
            return redirect('room', pk=message.room.id)
        if message.chat:
            return redirect('chat', pk=message.chat.id)
        if message.private_room:
            return redirect('private_room', pk=message.private_room.id)
    context = {'obj': message}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk=user.id)
    return render(request, 'base/update_user.html', {'form': form})


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    paginator = Paginator(topics, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'topics': topics, 'page_obj': page_obj}
    return render(request, 'base/topics.html', context)


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required(login_url='login')
def edit_message(request, pk):
    messg = Message.objects.get(id=pk)
    form = MessageForm(instance=messg)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=messg)
        if form.is_valid():
            form.save()
        if messg.room:
            return redirect('room', messg.room.id)
        if messg.chat:
            return redirect('chat', messg.chat.id)
        if messg.private_room:
            return redirect('private_room', messg.private_room.id)
    context = {'form': form, 'messg': messg}
    return render(request, 'base/edit_mess_form.html', context)


@login_required(login_url='login')
def reply_message(request, pk):
    messg = Message.objects.get(id=pk)
    form = MessageForm()
    pow = 'Message.objects.get(id=messg.id)'
    if request.method == 'POST':
        if messg.room:
            messag = Message.objects.create(
                user=request.user,
                room=messg.room,
                body=request.POST.get('body'),
                reply=messg.id
            )
            return redirect('room', messg.room.id)
        elif messg.private_room:
            messag = Message.objects.create(
                user=request.user,
                private_room=messg.private_room,
                body=request.POST.get('body'),
                reply=messg.id
            )
            return redirect('private_room', messg.private_room.id)
        else:
            messag = Message.objects.create(
                user=request.user,
                chat=messg.chat,
                body=request.POST.get('body'),
                reply=messg.id
            )
            return redirect('chat', messg.chat.id)
    context = {'form': form, 'messg': messg, 'pow': pow}
    return render(request, 'base/reply_messg.html', context)


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
    return render(request, 'base/profile.html', context)
