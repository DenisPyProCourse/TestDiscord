from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render

from private_message.models import Chat
from private_room.models import Private_Room
from room.models import Room
from .forms import MessgImg, MessageForm
from .models import Topic, Message


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


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    paginator = Paginator(topics, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'topics': topics, 'page_obj': page_obj}
    return render(request, 'base/topics.html', context)


def activity_page(request):
    room_messages = Message.objects.select_related('room').all()
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
