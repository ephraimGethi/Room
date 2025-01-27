from django.shortcuts import render,redirect

# Create your views here.
from django.http import HttpResponse
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.http import HttpResponse
# rooms = [
#     {"id":1,"name":"lets learn python"},
#     {"id":2,"name":"lets design database"},
#     {"id":3,"name":"backend developers "},

# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()   
        password = request.POST.get('password') 

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'user does not exist')
        
        user = authenticate(request,username = username,password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username Or Password does not exist')

    context = {"page":page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"an error occurred during registration")

    context ={"form":form}
    return render(request,'base/login_register.html',context)

def home(request):
    rooms = Room.objects.all()
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q)
                                 | Q(name__icontains = q)
                                   | Q(description__icontains = q)
                                     | Q(host__username__icontains = q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    context = {"rooms":rooms,"topics":topics,"room_count":room_count,"room_messages":room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
    rooms = Room.objects.get(id = pk) 
    room_messages = rooms.message_set.all().order_by('-created')  
    participants = rooms.participants.all()


    if request.method == 'POST':
        message =  Message.objects.create(
            user = request.user,
            room = rooms,
            body = request.POST.get('body')
                   )
        rooms.participants.add(request.user)
        
        return redirect('room',pk=rooms.id)
    context = {'room':rooms,'room_messages':room_messages,'participants':participants}
    # context = {"context":rooms[pk]}
    return render(request,'base/room.html',context)


def userProfile(request,pk):

    user = User.objects.get(id = pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user":user,
               "rooms":rooms,
               "topics":topics,
               "room_messages":room_message,}
    return render(request,'base/profile.html',context)

@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )                 
        return redirect('home')
    context = {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url = 'login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    form2 = UserChangeForm()
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        form = RoomForm(request.POST,instance= room)
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic         
        room.description = request.POST.get('description')
        room.save() 
        return redirect('home')
    context = {'form':form,'topics':topics,'room':room,'form2':form2}

    return render(request,'base/room_form.html',context)

@login_required(login_url = 'login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url = 'login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk = user.id)
    return render(request,'base/edit-user.html',{'form':form})


def topicsPage(request):
    topic = request.GET.get('topic') if request.GET.get('topic') != None else ''
    topicsCount = Topic.objects.all().count()
    topics = Topic.objects.filter(name__icontains = topic)[0:3]
    return render(request,'base/topics.html',{"topics":topics,"count":topicsCount})


def activityPage(request):

    room_messages = Message.objects.all()[0:3]

    return render(request,'base/activity.html',{"room_messages":room_messages})