from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import MyUserCreationForm, MessageForm, ChatForm, MessgImg
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
    img = MessageForm()
    participants = room.participants.all()
    if request.method == "POST":
        msg = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
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
        # img = add_image(request=request, pk=room.id)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'msgs': msgs,
        'participants': participants,
        'img': img
    }
    return render(request, 'base/room.html', context)





@login_required(login_url='login')
def private_messages(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    chats = Chat.objects.filter(members=request.user.id).order_by('-updated')
    users = []
    for i in chats:
        # print(i.members.all())
        for j in i.members.all():
            if j.id != request.user.id:
                usern = User.objects.get(id=j.id) #Mb not final solution
                users.append(usern)
    # print(users)


    context = {
        'user': user,
        'chats': chats,
        'topics': topics,
        'room_messages': room_messages,
        'users': users
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
    pow = 'Message.objects.get(id=messg.id)'
    if request.method == 'POST':
        if messg.room:
            messg = Message.objects.create(
                user=request.user,
                room=messg.room,
                body=request.POST.get('body'),
                reply=messg
            )
            # pow = Message.objects.get(id=messg.reply)
            return redirect('room', messg.room.id)
        else:
            messg = Message.objects.create(
                user=request.user,
                chat=messg.chat,
                body=request.POST.get('body'),
                reply=messg
            )
            # pow = Message.objects.get(id=messg.reply)
            return redirect('chat', messg.chat.id)
    context = {'form': form, 'messg': messg, 'pow': pow}
    return render(request, 'base/reply_messg.html', context)

