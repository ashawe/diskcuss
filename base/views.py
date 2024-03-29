from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# Create your views here.

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user = authenticate(request,username=username,password=password)        
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username or Password incorrect')
        except:
            messages.error(request, 'Username or Password incorrect')

    context = {'page':'login'}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Error while registering. Please check all fields and try again.')
    context = {'page':'register', 'form':form}
    return render(request, 'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    room_count = rooms.count()
    topics = Topic.objects.all().annotate(num_posts=Count('room')).order_by('-num_posts')[0:5]
    if request.user.is_authenticated:
        room_messages = Message.objects.all().exclude(user=request.user)
    else:
        room_messages = Message.objects.all() 

    context = {'rooms' : rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request,'base/home.html', context)

def room(request,pk):
    selectedRoom = Room.objects.get(id=pk)
    messages = selectedRoom.message_set.all()
    participants = selectedRoom.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=selectedRoom,
            body=request.POST.get('body')
        )
        selectedRoom.participants.add(request.user)
        return redirect('room',pk=selectedRoom.id)

    context = {'room' : selectedRoom, 'roomMessages':messages, 'participants':participants}
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all().annotate(num_posts=Count('room')).order_by('-num_posts')[0:5]
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        room.participants.add(request.user)
        room.save()
        return redirect('home')
    context  = {'form':form, 'page':'Create', 'topics':topics}
    return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        messages.error(request,'Bad Request')
        return redirect('home')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context  = {'form':form, 'page':'Update', 'topics':topics, 'room_topic':room.topic.name}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        messages.error(request,'Bad Request')
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        messages.error(request,'Bad Request')
        return redirect('home')

    if request.method == 'POST':
        roomid = message.room.id
        message.delete()
        return redirect('room',pk=roomid)
    return render(request, 'base/delete.html',{'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context = {'form':form}
    return render(request,'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q).annotate(num_posts=Count('room')).order_by('-num_posts')
    context = {'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request,'base/activity.html',context)