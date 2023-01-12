import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import RoomForm
from .models import Room
from base.models import Message, Topic


def room(request, pk):
    room = Room.objects.get(id=pk)
    msgs = room.message_set.all()
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
        room.participants.add(request.user)
        room.updated = msg.created
        room.save()
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'msgs': msgs,
        'participants': participants,
        'mesag': mesag
    }
    return render(request, 'room/room.html', context)


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
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'room/room_form.html', context)


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
        return redirect('room', pk=room.id)
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'room/room_form.html', context)


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
