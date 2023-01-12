from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from .models import Friends
from room.models import Room
from base.models import Topic, Message
from accounts.models import User


@login_required(login_url='login')
def add_friend(request, pk):
    user_friend = User.objects.get(id=pk)
    if request.method == 'POST':
        friend = Friends.objects.create(host_friend=request.user)
        friend.friend.add(request.user)
        friend.friend.add(user_friend)
        return redirect('user_profile', pk=user_friend.id)
    return render(request, 'friends/add_friend.html', context={'user_friend': user_friend})


def delete_friend(request, pk):
    friend = Friends.objects.get(id=pk)
    if request.method == 'POST':
        friend.delete()
        return redirect('friends_list')
    return render(request, 'base/delete.html', context={'obj': friend})


def friend_request(request, pk):
    connection = Friends.objects.get(id=pk)
    user_friend = User.objects.filter(friends=connection)
    if request.method == 'POST':
        connection.is_friend = True
        connection.save()
        return redirect('friends_list')
    return render(request, 'friends/add_friend.html', context={'connection': connection, 'user_friend': user_friend})


def friends_list(request):
    connection = Friends.objects.filter(friend=request.user.id)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__first_name__icontains=q)
    )
    topics = Topic.objects.all()[0:10]
    friends_count = connection.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:7]
    context = {
        'connection': connection,
        'rooms': rooms,
        'topics': topics,
        'friends_count': friends_count,
        'room_messages': room_messages
    }
    return render(request, 'friends/friends_list.html', context)
