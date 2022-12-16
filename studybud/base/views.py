import datetime
import signal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import MyUserCreationForm, MessageForm, ChatForm
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RoomForm, UserForm
from .models import Room, Topic, Message, User, Chat
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator


# rooms = [
#     {'id': 1, 'name': 'Let\'s learn Python'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]
from .token import account_activation_token


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
            # user.username = user.username.lower()
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
            # return HttpResponse('Please confirm your email address to complete the registration')
            # login(request, user)
            #
            # redirect('home')
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
        return render(request,'base/email_confirmation.html', context= {'em_log': em_log}) #'Thank you for your email confirmation. Now you can login your account.'
    else:
        return HttpResponse('Activation link is invalid!')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__first_name__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    # if receiver(post_save, sender=User):
    #     if created:
    #         messages.error(request, 'Email')

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)

def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    # msgs = room.message_set.all().order_by('-created') # I'll add ordering at model Meta class instead of writing it here
    msgs = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        msg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'msgs': msgs,
        'participants': participants
    }
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def private_messages(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    chats = Chat.objects.filter(members=request.user.id).order_by('-updated')
    for i in chats:
        for j in i.members.all():
            if j.id != request.user.id:
                user = User.objects.get(id=j.id) #НЕ СДЕЛАЛ, подтягивается то один то другой участник
                

    context = {
        'user': user,
        'chats': chats,
        'topics': topics,
        'room_messages': room_messages
    }
    return render(request, 'base/private_messages.html', context)

# def create_chat(request, pk):
#     user = User.objects.get(id=pk)
#     form = ChatForm()
#     chats = Chat.objects.filter(members__in=[request.user.id, user.id]).annotate(
#         c=Count('members')).filter(c=2)
#     if request.method == 'POST':
#         if chats.count() == 0:
#             chats = Chat.objects.create(
#                 name=request.POST.get('name')
#             )
#             chats.members.add(request.user)
#             chats.members.add(user)
#             return redirect('chat', pk=chats.id)
#         else:
#             chats = chats.first()
#             return redirect('chat', pk=chats.id)
#             # print(chats)
#             # return redirect('chat', pk=chats.id)
#     return render(request, 'base/chat_form.html', context={'user': user, 'form': form, 'chats': chats})

def create_chat(request, pk):
    user = User.objects.get(id=pk)
    form = ChatForm()
    if request.method == 'POST':
            chat = Chat.objects.create(
                name=request.POST.get('name')
            )
            chat.members.add(request.user)
            chat.members.add(user)
            return redirect('chat', pk=chat.id)
        # else:
        #     chats = chats.first()
        #     return redirect('chat', pk=chats.id)
            # print(chats)
            # return redirect('chat', pk=chats.id)
    return render(request, 'base/chat_form.html', context={'user': user, 'form': form})

def chat(request, pk):
    chat = Chat.objects.get(id=pk)
    msgs = chat.message_set.all()
    members = chat.members.all()
    if request.method == "POST":
        msg =Message.objects.create(
            user=request.user,
            chat=chat,
            body=request.POST.get('body'),
        )
        # chat.updat = msg.created
        # if msg:
        #     chat.updated.now()
        chat.updated = msg.created
        chat.save()
        return redirect('chat', pk=chat.id)
    context = {
        'chat': chat,
        'msgs': msgs,
        'members': members
    }
    return render(request, 'base/chat.html', context)

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_count = rooms.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[0:5]
    # dialog = user.chat_set.
    # chats = Chat.objects.get(pk=2)
    chats = Chat.objects.filter(members__in=[request.user.id, user.id]).annotate(
        c=Count('members')).filter(c=2)
    if request.method == 'POST':
        if chats.count() == 0:
            create_chat(pk=pk)
        else:
            chats = chats.first()
    chats = chats.first()
            # return redirect('chat', pk=chats.id)
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'room_count': room_count,
        'chats': chats
    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        #       return redirect('home')

        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowe here!!!')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
        return redirect('room', pk=room.id)
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowe here!!!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)

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
        return redirect('room', pk=message.room.id)
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
        # else:
        #     form = UserForm(request.POST, request.FILES, instance=user)

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
        return redirect('room', messg.room.id)
    context = {'form': form, 'messg': messg}
    return render(request, 'base/edit_mess_form.html', context)

@login_required(login_url='login')
def reply_message(request, pk):
    messg = Message.objects.get(id=pk)
    form = MessageForm(instance=messg)
    pow = Message.objects.get(id=pk)
    if request.method == 'POST':
        messg = Message.objects.create(
            user=request.user,
            room=messg.room,
            body=request.POST.get('body'),
            reply=messg
        )
        # s = messg.reply__user
        return redirect('room', messg.room.id)
    context = {'form': form, 'messg': messg, 'pow': pow}
    return render(request, 'base/reply_messg.html', context)

#
# def dial_view(request):
#     chats = Chat.objects.filter(members__in=[request.user.id])
#     return render(request, 'base/dialoges.html', {'user_profile': request.user, 'chats': chats})
#
# def priv_mess_view(request, chat_id):
#     if request.method == "GET":
#         try:
#             chat = Chat.objects.get(id=chat_id)
#             if request.user in chat.members.all():
#                 chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
#             else:
#                 chat = None
#         except Chat.DoesNotExist:
#             chat = None
#
#         return render(
#             request,
#             'base/priv_messg.html',
#             {
#                 'user_profile': request.user,
#                 'chat': chat,
#                 'form': MessageForm()
#             }
#         )
#     elif request.method == "POST":
#         form = PrivateMessageForm(data=request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.chat_id = chat_id
#             message.author = request.user
#             message.save()
#         return redirect(reverse('users:messages', kwargs={'chat_id': chat_id}))
#
# def create_dialog_viwe(request):
#     # if request.method == "POST":
#     #     add_user = request.POST.get('profile')
#     #     chats = Chat.objects.filter(members__in=[request.user.id, add_user], type=Chat.DIALOG).annotate(
#     #         c=Count('members')).filter(c=2)
#     #     if chats.count() == 0:
#     #         chat = Chat.objects.create()
#     #         chat.members.add(request.user)
#     #         chat.members.add(add_user)
#     #     else:
#     #         chat = chats.first()
#     #
#     #     return render(request, 'base/create_dialog.html', context={'add_user': add_user})
#     # form = DialogForm()
#     # topics = Topic.objects.all()
#     if request.method == 'POST':
#         add_user = request.POST.get('profile')
#         chats = Chat.objects.filter(members__in=[request.user.id, add_user], type=Chat.DIALOG).annotate(
#             c=Count('members')).filter(c=2)
#         # topic_name = request.POST.get('topic')
#         # topic, created = Topic.objects.get_or_create(name=topic_name)
#         if chats.count() == 0:
#             chat = Chat.objects.create()
#             chat.members.add(request.user)
#             chat.members.add(add_user)
#         else:
#             chat = chats.first()
#             # host=request.user,
#             # topic=topic,
#             # name=request.POST.get('name'),
#             # description=request.POST.get('description')
#         # )
#         # form = RoomForm(request.POST)
#         # if form.is_valid():
#         #     room = form.save(commit=False)
#         #     room.host = request.user
#         #     room.save()
#         #       return redirect('home')
#
#         return redirect('home')
#     context = {}
#     return render(request, 'base/create_dialog.html', context)
#
# def dialog(request, pk):
#     chats = Chat.objects.get(id=pk)
#         # msgs = room.message_set.all().order_by('-created') # I'll add ordering at model Meta class instead of writing it here
#     msgs = chats.message_set.all()
#     # participants = room.participants.all()
#     if request.method == "POST":
#         msg = Message.objects.create(
#             author=request.user,
#             chat=dialog,
#             message=request.POST.get('message')
#         )
#         # room.participants.add(request.user)
#         return redirect('dialogs', pk=chats)
#     context = {
#         'chats': chats,
#         'msgs': msgs,
#         # 'participants': participants
#     }
#     return render(request, 'base/dialoges.html', context)