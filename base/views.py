from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.core.exceptions import PermissionDenied

# Create your views here.T


def permissionDeniedView(request):
    raise PermissionDenied


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password").lower()

        try:
            user = User.objects.get(username=username)
        except:  # noqa: E722
            messages.error(request, "User does not exist.")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username OR password does not exist.")
    context = {"page": page}

    return render(request, "base/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerUser(request):
    form = UserCreationForm()

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user)
                return redirect("home")
            except Exception as e:
                print(f"Registration failed. Error: {e}")
        else:
            messages.error(request, "The form is invalid")

    context = {"form": form}

    return render(request, "base/signup.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__contains=q) | Q(description__contains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    rooms_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "rooms_message": rooms_message,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="/login")
def createRoom(request):

    form = RoomForm()
    topic = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("room", pk=room.id)

    context = {"form": form, "topics": topic}
    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.topic = topic
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.save()
        return redirect("room", pk=room.id)

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        HttpResponse("Your are not allowed here!")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    context = {"obj": room}
    return render(request, "base/delete.html", context)


@login_required(login_url="/login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        HttpResponse("Your are not allowed here!")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    context = {"obj": message}
    return render(request, "base/delete.html", context)


@login_required(login_url="/login")
def updateUser(request, pk):

    user = User.objects.get(id=pk)
    form = UserForm(instance=user)

    if request.user == user:

        if request.method == "POST":
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                try:
                    form.save()
                    return redirect("user-profile", pk=user.id)
                except Exception as e:
                    return Exception(f"Registration failed. Error: {e}")
            else:
                messages.error(request, "The form is invalid")

    elif request.user != user:
        return permissionDeniedView(request)
        
    context = {"form": form}
    return render(request, "base/update-user.html", context)


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def activityPage(request):
    room_messages = Message.objects.all()

    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)