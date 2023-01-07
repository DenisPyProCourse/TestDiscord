import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import MyUserCreationForm, MessageForm, ChatForm, MessgImg, PrivateRoomForm, PrivateRoomFormCreate
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RoomForm, UserForm
from .models import Room, Topic, Message, User, Chat, Friends, Private_Room
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
    ).order_by('-updated')
    topics = Topic.objects.all().order_by('-updated')[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:10]
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

def add_image(request, pk):
    room, chat = None, None
    img = MessgImg()
    print(request, "!!!!!!!")
    if 'room' in request.path:
        print('room in Request')
    else:
        print('no!!!!')
    if 'room' in request.path:
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

    # if request.method == 'POST':
    #         img = MessgImg(request.POST, request.FILES, instance=Message.objects.create(
    #         user=request.user,
    #         body='',
    #         room=room
    #     ))
    #         if img.is_valid():
    #             img.save()
    #             return redirect('room', room.id)
    #     else:
            # img = MessgImg(request.POST, request.FILES, instance=Message.objects.create(
            #     user=request.user,
            #     body='',
            #     chat=chat
            # ))
            # if img.is_valid():
            #     img.save()
            #     return redirect('chat', chat.id)
    return render(request, 'base/add_image.html', {'img': img, 'room': room, 'chat': chat})

def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    # msgs = room.message_set.all().order_by('-created') # I'll add ordering at model Meta class instead of writing it here
    msgs = room.message_set.all()
    # img = MessageForm()
    participants = room.participants.all()
    ids = []
    for i in msgs:
        if i.reply:
            ids.append(i.reply)
    mesag = Message.objects.filter(id__in=ids)
    if request.method == "POST":
        msg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        # room.updated = msg.created
        # room.save()
        # img = MessageForm(request.POST, request.FILES)
        # if img.is_valid():
        #     # img.save()
        #     msg2 = Message.objects.create(
        #         user=request.user,
        #         room=room,
        #         body=None,
        #         images=img.images
        #     )
        #     msg2.save()
        room.participants.add(request.user)
        room.updated = msg.created
        room.save()
        # img = add_image(request=request, pk=room.id)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'msgs': msgs,
        'participants': participants,
        'mesag': mesag
    }
    return render(request, 'base/room.html', context)

def priv_room_add_friends(request, pk):
    priv_room = Private_Room.objects.get(id=pk)
    # print(priv_room.name)
    form = PrivateRoomFormCreate(instance=priv_room)
    # print(form.instance.host)
    # print(form.fields['name'])
    # print(form.fields['name'])
    if request.method == 'POST':
        form = PrivateRoomFormCreate(request.POST, instance=priv_room)
        # print(form.instance.host)
        # print(form.instance.name)
        # form = form(request.POST)
        # print(form.clean().get('name'))
        # print(form['name'])
        # form.description = priv_room.description
        # form.
        # form.get_context()
        # form.instance = PrivateRoomForm(instance=priv_room)
        if form.is_valid():
            # print('KKKKKKKKK!!!')
            rm = form.save(commit=False)
            temp = form.cleaned_data.get("room_friends")
            for i in temp:
                # print(i)
                priv_room.room_friends.add(User.objects.get(id=i))
                priv_room.save()
            priv_room.save()
            rm.save()

            return redirect('private_room', priv_room.id)
        else:
            print(form.errors)
    context = {'form': form, 'priv_room': priv_room}
    return render(request, 'base/priv_room_add_friends.html', context)

def priv_room_delete_friends(request, rm_pk, us_pk):
    friend = User.objects.get(id=us_pk)
    priv_room = Private_Room.objects.get(id=rm_pk)
    # print(priv_room.room_friends.get(id=friend.id))
    if request.method == 'POST':
        priv_room.room_friends.remove(friend)
        return redirect('private_room', priv_room.id)
    context = {'obj': friend}
    return render(request, 'base/delete.html', context)
#

def private_room(request, pk):
    priv_room = Private_Room.objects.get(id=pk)
    msgs = priv_room.message_set.all()
    friends = priv_room.room_friends.all()
    ids = []
    for i in msgs:
        if i.reply:
            ids.append(i.reply)
    mesag = Message.objects.filter(id__in=ids)
    if request.method == "POST":
        msg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body'))

        priv_room.updated = msg.created
        priv_room.save()
        return redirect('private_room', pk=priv_room.id)
    context = {
        'priv_room': priv_room,
        'msgs': msgs,
        'friends': friends,
        'mesag': mesag
    }
    return render(request, 'base/private_room.html', context)

# @login_required(login_url='login')
# def create_private_room(request):
#     # form = PrivateRoomFormCreate()
#     # form.host = r
#     # friends = Friends.objects.filter(Q(is_friend=True) |
#     #                                 Q(host_friend_id=request.user.id))
#     # host = request.user
#     form = PrivateRoomFormCreate(instance=request.user)
#     # form.fields['host'] = request.user
#     # form.fields['host'] = request.user
#     if request.method == 'POST':
#         # friends_name = request.POST.get('friends')
#         # friends = Friends.objects.get(friend__username=friends_name)
#         # topic_name = request.POST.get('topic')
#         # topic, created = Topic.objects.get_or_create(name=topic_name)
#         # Private_Room.objects.create(
#         #     host=request.user
#         #     friends=Friends.objects.filter(Q(is_friend=True) |
#         #                             Q(host_friend_id=request.user.id)),
#         #     name=request.POST.get('name'),
#         #     description=request.POST.get('description')
#         # )
#         # topic.updated = datetime.datetime.now()
#         # topic.save()
#         form = PrivateRoomFormCreate(request.POST)
#         # form.fields['friends'].choices = Friends.objects.filter(Q(is_friend=True) |
#         #                             Q(host_friend=request.user))
#         # form.fields['friends'].choices = friends
#         if form.is_valid():
#             # form.save()
#             priv_room = form.save(commit=False)
#             priv_room.host = request.user
#
#             # for i in form.fields['room_friends']:
#             # print(priv_room.room_friends.all())
#             # for i in priv_room.room_friends:
#             #     print(i)
#             # priv_room.room_friends
#             # priv_room.name = request.POST.get('name')
#             # priv_room.description = request.POST.get('description')
#             # print(temp)
#             priv_room.save()
#             priv_room.room_friends.add(request.user.id)
#             temp = form.cleaned_data.get("room_friends")
#             for i in temp:
#                 priv_room.room_friends.add(User.objects.get(id=i))
#             # priv_room.room_friends.add(request.user)
#
#             # priv_room.people.add((i for i in friends.id))
#             # for i in friends:
#             #     print(User.objects.filter(friends__in=friends))
#             #     priv_room.people.add(i)
#
#         #     room.save()
#         #       return redirect('home')
#
#         return redirect('private_messages', request.user.id)
#     context = {'form': form}
#     return render(request, 'base/private_room_form.html', context)

@login_required(login_url='login')
def create_private_room(request):
    # form = PrivateRoomFormCreate()
    # form.host = r
    # friends = Friends.objects.filter(Q(is_friend=True) |
    #                                 Q(host_friend_id=request.user.id))
    # host = request.user
    form = PrivateRoomForm()
    # form.fields['host'] = request.user
    # form.fields['host'] = request.user
    if request.method == 'POST':
        # friends_name = request.POST.get('friends')
        # friends = Friends.objects.get(friend__username=friends_name)
        # topic_name = request.POST.get('topic')
        # topic, created = Topic.objects.get_or_create(name=topic_name)
        # Private_Room.objects.create(
        #     host=request.user
        #     friends=Friends.objects.filter(Q(is_friend=True) |
        #                             Q(host_friend_id=request.user.id)),
        #     name=request.POST.get('name'),
        #     description=request.POST.get('description')
        # )
        # topic.updated = datetime.datetime.now()
        # topic.save()
        form = PrivateRoomForm(request.POST)
        # form.fields['friends'].choices = Friends.objects.filter(Q(is_friend=True) |
        #                             Q(host_friend=request.user))
        # form.fields['friends'].choices = friends
        if form.is_valid():
            # form.save()
            priv_room = form.save(commit=False)
            priv_room.host = request.user

            # for i in form.fields['room_friends']:
            # print(priv_room.room_friends.all())
            # for i in priv_room.room_friends:
            #     print(i)
            # priv_room.room_friends
            # priv_room.name = request.POST.get('name')
            # priv_room.description = request.POST.get('description')
            # print(temp)
            priv_room.save()
            priv_room.room_friends.add(request.user.id)
            # temp = form.cleaned_data.get("room_friends")
            # for i in temp:
            #     priv_room.room_friends.add(User.objects.get(id=i))
            # priv_room.room_friends.add(request.user)

            # priv_room.people.add((i for i in friends.id))
            # for i in friends:
            #     print(User.objects.filter(friends__in=friends))
            #     priv_room.people.add(i)

        #     room.save()
        #       return redirect('home')

            return redirect('add_friend_pr_r', priv_room.id)
    context = {'form': form}
    return render(request, 'base/private_room_form.html', context)

def update_private_room(request, pk):
    private_room = Private_Room.objects.get(id=pk)
    form = PrivateRoomFormCreate(instance=private_room)

    if request.method == 'POST':
        form = PrivateRoomFormCreate(request.POST)
        private_room.name = request.POST.get('name')
        temp = form.cleaned_data.get("room_friends")
        for i in temp:
            private_room.room_friends.add(User.objects.get(id=i))
        private_room.save()

        return redirect('private_room', pk=private_room.id)
    context = {'form': form, 'private_room': private_room}
    return render(request, 'base/private_room_form.html', context)

def private_rooms_list(request):
    private_rooms = Private_Room.objects.filter(room_friends=request.user)

    return render(request, 'base/private_rooms_list.html', context={'private_rooms': private_rooms})


@login_required(login_url='login')
def private_messages(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    chats = Chat.objects.filter(members=request.user.id).order_by('-updated')
    users = User.objects.filter(members__members=request.user.id)
    # private_rooms = Private_Room.objects.filter(host=request.user)
    # private_room()
    # users = []
    # for i in chats:
    #     # print(i.members.all())
    #     for j in i.members.all():
    #         if j.id != request.user.id:
    #             usern = User.objects.get(id=j.id) #Mb not final solution
    #             users.append(usern)
    # print(users)


    context = {
        'user': user,
        'chats': chats,
        'topics': topics,
        'room_messages': room_messages,
        'users': users,
        # 'private_rooms': private_rooms
    }
    return render(request, 'base/private_messages.html', context)


def create_chat(request, pk):
    user = User.objects.get(id=pk)
    form = ChatForm()
    if request.method == 'POST':
            chat = Chat.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description')
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
    ids = []
    for i in msgs:
        if i.reply:
            ids.append(i.reply)
    mesag = Message.objects.filter(id__in=ids)
    if request.method == "POST":
        msg =Message.objects.create(
            user=request.user,
            chat=chat,
            body=request.POST.get('body'),
        )
        chat.updated = msg.created
        chat.save()
        return redirect('chat', pk=chat.id)
    context = {
        'chat': chat,
        'msgs': msgs,
        'members': members,
        "mesag": mesag
    }
    return render(request, 'base/chat.html', context)

def update_chat(request, pk):
    chat = Chat.objects.get(id=pk)
    form = ChatForm(instance=chat)

    if request.method == 'POST':
        chat.name = request.POST.get('name')
        chat.save()

        return redirect('chat', pk=chat.id)
    context = {'form': form, 'chat': chat}
    return render(request, 'base/chat_form.html', context)

@login_required(login_url='login')
def delete_chat(request, pk):
    chat = Chat.objects.get(id=pk)
    if request.method == 'POST':
        chat.delete()
        return redirect('home')
    context = {'obj': chat}
    return render(request, 'base/delete.html', context)


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
        topic.updated = datetime.datetime.now()
        topic.save()
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
    pow = 'Message.objects.get(id=messg.id)'
    if request.method == 'POST':
        if messg.room:
        #     { % if msg.reply %}
        #     { %
        #     for i in mesag %}
        #     { % if i.reply == msg.reply %}
        #     < a
        #     href = "#{{  msg.reply }}" > Replied
        #     to: "{{i}}..." < / a >
        # {  # <label for="{{ msg.reply }}">Replied to: "{{ msg.reply }}..."</label>#}
        #     { % endif %}
        # { % endfor %}
        # { % endif %}
            messag = Message.objects.create(
                user=request.user,
                room=messg.room,
                body=request.POST.get('body'),
                reply=messg.id
            )
            # print(messg.objects.get())
            # pow = Message.objects.get(id=messg.reply)
            return redirect('room', messg.room.id)
        else:
            messag = Message.objects.create(
                user=request.user,
                chat=messg.chat,
                body=request.POST.get('body'),
                reply=messg.id
            )
            # pow = Message.objects.get(id=messg.reply)
            return redirect('chat', messg.chat.id)
    context = {'form': form, 'messg': messg, 'pow': pow}
    return render(request, 'base/reply_messg.html', context)

def add_friend(request, pk):
    user_friend = User.objects.get(id=pk)
    # form = ChatForm()
    if request.method == 'POST':
        friend = Friends.objects.create(host_friend=request.user)
        friend.friend.add(request.user)
        friend.friend.add(user_friend)
        # friend.host_friend = request.user
        # friend.is_friend = True
        return redirect('user_profile', pk=user_friend.id)
    # return HttpResponse('SSS')
    # user_friend = User.objects.get(id=pk)
    # friends = Friends.objects.filter(friend__in=[request.user.id, user_friend.id]).annotate(
    #     c=Count('friend')).filter(c=2)
    # if request.method == 'POST':
    #     if friends.count() == 2:
    #         if friends.first().is_friend == False:
    #             friends.first().is_friend = True
    #         else:
    #             friends.first().is_friend = False
    #     else:
    #         friend = Friends.objects.create(
    #             is_friend=True
    #         )
    #         friend.friend.add(request.user)
    #         friend.friend.add(user_friend)
    #         return redirect('user_profile', user_friend.id)
    return render(request, 'base/add_friend.html', context={'user_friend': user_friend})
    # return redirect('user_profile', user.id)

def delete_friend(request, pk):
    friend = Friends.objects.get(id=pk)
    if request.method == 'POST':
            friend.delete()
            return redirect('friends_list')
    return render(request, 'base/delete.html', context={'obj': friend})

def friend_request(request, pk):
    connection = Friends.objects.get(id=pk)
    # print(connection)
    # user = User.objects.get(id=connection.friend)
    user_friend = User.objects.filter(friends=connection)
    if request.method == 'POST':
        connection.is_friend = True
        connection.save()
        return redirect('friends_list')
    return render(request, 'base/add_friend.html', context={'connection': connection, 'user_friend': user_friend})

def friends_list(request):
    connection = Friends.objects.filter(friend=request.user.id)
    # if request.method == 'POST':
    friends = User.objects.filter(friends__friend=request.user.id)
    for i in connection:
        for j in i.friend.all():
            # if j.id != request.user.id:
                print(j.id)
    # for i in connection:
    #     print(i.id)

    # chats = Chat.objects.filter(members=request.user.id).order_by('-updated')
    # for i in friends:
    #     i.friends.
    #     users = User.objects.filter(id=friends)
    # print(friends)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__first_name__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    friends_count = friends.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    # if receiver(post_save, sender=User):
    #     if created:
    #         messages.error(request, 'Email')

    context = {
        'friends': friends,
        # 'users': users,
        'connection': connection,
        'rooms': rooms,
        'topics': topics,
        'friends_count': friends_count,
        'room_messages': room_messages
        # 'chats': chats
    }
    return render(request, 'base/friends_list.html', context)

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
    # print(friends.id)
    print(chats)
    # print(friends.first().friend)
    # if request.method == 'POST':
    #     if friends.count() == 2:
    #         if friends.first().is_friend == False:
    #             friends.first().is_friend = True
    #         else:
    #             friends.first().is_friend = False
    #     else:
    #         friend = Friends.objects.create(
    #             is_friend=True
    #         )
    #         friend.friend.add(request.user)
    #         friend.friend.add(user_friend)
    #         return redirect('user_profile', user_friend.id)
    # add_friend(request=request, pk=pk)
    if request.method == 'POST':
        if chats.count() == 0:
            create_chat(pk=pk)
        else:
            chats = chats.first()
        # if friends.first() is None:
        #     add_friend(pk=pk)
        # else:
        #     if friends.first().is_friend == False:
        #         friends.first().is_friend = True
        #     else:
        #         friends.first().is_friend = False


    chats = chats.first()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'room_count': room_count,
        'chats': chats,
        'friends': friends
    }
    return render(request, 'base/profile.html', context)