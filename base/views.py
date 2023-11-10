from django.shortcuts import render
from .models import Room

# Create your views here.

rooms = Room.objects.all()

def home(request):
    
    context = {'rooms' : rooms}
    return render(request,'base/home.html', context)

def room(request,pk):
    selectedRoom = Room.objects.get(id=pk)
    context = {'room' : selectedRoom}
    return render(request,'base/room.html',context)