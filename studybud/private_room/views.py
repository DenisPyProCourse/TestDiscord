from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import PrivateRoomFormCreate, PrivateRoomForm
from .models import Private_Room
from base.models import Message, Topic
from accounts.models import User


def priv_room_add_friends(request, pk):
    priv_room = Private_Room.objects.get(id=pk)
    form = PrivateRoomFormCreate(instance=priv_room)
    if request.method == 'POST':
        form = PrivateRoomFormCreate(request.POST, instance=priv_room)
        if form.is_valid():
            rm = form.save(commit=False)
            temp = form.cleaned_data.get("room_friends")
            for i in temp:
                priv_room.room_friends.add(User.objects.get(id=i))
                priv_room.save()
            priv_room.save()
            rm.save()
            return redirect('private_room', priv_room.id)
    context = {'form': form, 'priv_room': priv_room}
    return render(request, 'private_room/priv_room_add_friends.html', context)


def priv_room_delete_friends(request, rm_pk, us_pk):
    friend = User.objects.get(id=us_pk)
    priv_room = Private_Room.objects.get(id=rm_pk)
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
            private_room=priv_room,
            body=request.POST.get('body')
        )
        priv_room.updated = msg.created
        priv_room.save()
        return redirect('private_room', pk=priv_room.id)
    context = {
        'priv_room': priv_room,
        'msgs': msgs,
        'friends': friends,
        'mesag': mesag
    }
    return render(request, 'private_room/private_room.html', context)


@login_required(login_url='login')
def create_private_room(request):
    form = PrivateRoomForm()
    if request.method == 'POST':
        form = PrivateRoomForm(request.POST)
        if form.is_valid():
            priv_room = form.save(commit=False)
            priv_room.host = request.user
            priv_room.save()
            priv_room.room_friends.add(request.user.id)
            return redirect('add_friend_pr_r', priv_room.id)
    context = {'form': form}
    return render(request, 'private_room/private_room_form.html', context)


def update_private_room(request, pk):
    private_room = Private_Room.objects.get(id=pk)
    form = PrivateRoomForm(instance=private_room)
    if request.method == 'POST':
        form = PrivateRoomForm(request.POST)
        private_room.name = request.POST.get('name')
        private_room.save()
        return redirect('private_room', pk=private_room.id)
    context = {'form': form, 'private_room': private_room}
    return render(request, 'private_room/private_room_form.html', context)


@login_required(login_url='login')
def delete_private_room(request, pk):
    priv_room = Private_Room.objects.get(id=pk)
    if request.method == 'POST':
        priv_room.delete()
        return redirect('home')
    context = {'obj': priv_room}
    return render(request, 'base/delete.html', context)


def private_rooms_list(request):
    private_rooms = Private_Room.objects.filter(room_friends=request.user)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    users = User.objects.filter(room_friends__room_friends=request.user)
    topics = Topic.objects.all().order_by('-updated')[0:10]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    rooms_count = private_rooms.count()
    context = {
        'private_rooms': private_rooms,
        'topics': topics,
        'room_messages': room_messages,
        'rooms_count': rooms_count,
        'users': users
    }
    return render(request, 'private_room/private_rooms_list.html', context)
