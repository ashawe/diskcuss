from django.shortcuts import render

# Create your views here.

rooms = [
    { 
        'id' : 1,
        'name' : 'Dungeons & Dragons'
    },
    {
        'id' : 2,
        'name' : 'Monopoly'
    },
    {
        'id' : 3,
        'name' : 'Warhammer'
    }
]

def home(request):
    context = {'rooms' : rooms}
    return render(request,'base/home.html', context)

def room(request,pk):
    selectedRoom = None
    for room in rooms:
        if room['id'] == int(pk):
            selectedRoom = room
            break
    context = {'room' : selectedRoom}
    return render(request,'base/room.html',context)