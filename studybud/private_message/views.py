from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import ChatForm
from .models import Chat
from base.models import Topic, Message
from accounts.models import User


@login_required(login_url='login')
def private_messages(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    topics = Topic.objects.all().order_by('-updated')[0:10]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    chats = Chat.objects.filter(members=request.user.id).order_by('-updated')
    users = User.objects.filter(members__members=request.user.id)
    context = {
        'user': user,
        'chats': chats,
        'topics': topics,
        'room_messages': room_messages,
        'users': users
    }
    return render(request, 'private_message/private_messages.html', context)


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
    return render(request, 'private_message/chat_form.html', context={'user': user, 'form': form})


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
    return render(request, 'private_message/chat.html', context)


def update_chat(request, pk):
    chat = Chat.objects.get(id=pk)
    form = ChatForm(instance=chat)
    if request.method == 'POST':
        chat.name = request.POST.get('name')
        chat.save()
        return redirect('chat', pk=chat.id)
    context = {'form': form, 'chat': chat}
    return render(request, 'private_message/chat_form.html', context)


@login_required(login_url='login')
def delete_chat(request, pk):
    chat = Chat.objects.get(id=pk)
    if request.method == 'POST':
        chat.delete()
        return redirect('home')
    context = {'obj': chat}
    return render(request, 'base/delete.html', context)
