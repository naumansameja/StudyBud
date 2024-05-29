from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .form import RoomForm, UserForm, CustomUserCreationForm, DpForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from studybud import settings
from django.contrib.auth.tokens import default_token_generator

# Create your views here.
def home(request):
    q = request.GET.get("q")
    if not q:
        q = ""
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q))
    topics = Topic.objects.all()[:5]
    recent_messages = Message.objects.filter(room__topic__name__icontains=q).order_by('-created')


    return render(request,"base/home.html",{'rooms': rooms, "topics":topics, "recent_messages":recent_messages})

def room_page(request, pk):
    room = Room.objects.get(id=pk)
    
    # room_messages = Message.objects.filter(room__id=room.id).order_by("-created")
    room_messages = room.message_set.all()
    if request.method == "POST":
        if request.user.is_authenticated:
            Message.objects.create(
                body = request.POST.get('body'), 
                user = request.user,
                room = room
            )

        else:
            messages.error(request, "You must be logged in to send a message")
            return redirect('login')

    participants = room.participants.all()

    return render(request,"base/room.html", {"room": room, "room_messages":room_messages, "participants":participants})


def create_room(request):
    topics = Topic.objects.all()
    if request.user.is_authenticated:
        room_form = RoomForm()
        if request.method == "POST":
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            room = Room.objects.create(
                name = request.POST.get('name'),
                topic = topic,
                host = request.user,
                description = request.POST.get('description'),

            )
            return redirect("home")
    else:
        messages.error(request, "You must be logged in to create a room")
        return redirect('login')
    
    return render(request, "base/room_form.html", {"room_form":room_form, "topics":topics})

def join_room(request, roomid, userid):
    user = User.objects.get(id=userid)
    room = Room.objects.get(id=roomid)
    room.participants.add(user)
    return redirect('room', pk=room.id)


@login_required(login_url="login")
def update_room(request,pk):
    topics = Topic.objects.all()
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed to update this room")
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect("home")
    return render(request, "base/room_form.html", {"room_form":form, "topics":topics, 'room':room})

@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj":room})

def delete_message(request, origin, pk):
    del_message = Message.objects.get(id=pk)
    room = del_message.room

    if request.method == "POST":
        del_message.delete()
        if origin == 'room':
            return redirect(f"/room/{room.id}")
        elif origin == 'home':
            return redirect("home")
        elif origin == 'activity':
            return redirect("activity")

    return render(request, "base/delete.html", {"obj":del_message})

def user_login(request):
    page="login"
    user_exits_error = False
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]

        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            email = user.email
            

        except:
            user_exits_error = True
            messages.error(request, 'User does not exist')
            return redirect('login')
            

        user = authenticate(request, email=email , password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            if not user_exits_error:
                messages.error(request, 'Your password is incorrect')
    context = {"page":page}
    return render(request, "base/user-login.html", context)

# def user_register(request):
#     form = CustomUserCreationForm()
#     if request.method == "POST":
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = user.username.lower()
#             user.save()
#             login(request, user)
#             return redirect("upload", pk=user.id)
#         else:
#             messages.error(request, "Something went wrong.")
#     context = {"form":form}
#     return render(request, "base/user-login.html", context)






def user_logout(request):
    logout(request)
    return redirect("home")

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    messages = user.message_set.all()
    for message in messages:
        print(message)
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    context = {"rooms":rooms, 'recent_messages':messages, 'topics':topics, 'user':user}
    return render(request, 'base/user_profile.html', context)


def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        else:
            messages.error(request, "A user with this username already exists.")
            return redirect('update-user')   
    return render(request, 'base/update_user.html', {"form":form})


def topics_page(request):
    q = request.GET.get("q")
    if not q:
        q = ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics":topics}
    return render(request, 'base/topics.html', context)

def activity_page(request):
    messages = Message.objects.all()
    context = {"room_messages":messages}
    return render(request, 'base/activity.html', context)

def upload_picture(request, pk):
    user = User.objects.get(id=pk)

    form = DpForm(instance=user)
    if request.method == 'POST':
        form = DpForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.error(request, 'Something went wrong.')
    context = {'form':form}
    return render(request, 'base/profile_pic.html', context)

def change_password(request, pk):
    user = request.user
    if request.method == 'POST':
        if (not user.check_password(request.POST.get('old_password'))):
            messages.error(request, 'Old Password is not correct')
        
        elif request.POST.get('password1') != request.POST.get('password2'):
            messages.error(request, 'Passwords do not match')
        else:
            new_password = request.POST.get('password1')
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password updated successfully.')
    return render(request, 'base/change_password.html', {})
def user_register(request):
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()
            
            subject = "Welcome to Our Django User Registration System"
            message = f"Hello {user.first_name}!\n\nThank you for registering on our website. Please confirm your email address to activate your account.\n\nRegards,\nThe Django Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            # Send email confirmation link
            current_site = get_current_site(request)
            email_subject = "Confirm Your Email Address"
            message2 = render_to_string('base/email_confirmation.html', {
            'name': user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
            })
            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
            )
            email.send()
            messages.success(request, "Your account has been created successfully! Please check your email to confirm your email address and activate your account.")
    context = {'form':form}
    return render(request, "base/user-login.html", context)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your account has been activated!")
        return redirect('upload', pk=myuser.id)
    else:
        return HttpResponse('Something went wrong')

def reset_password_email_getter(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
        except:
            messages.error(request, "This email has not been registered here")
            return redirect('get-email')
        subject = "Welcome to Our Django User Reset Password System"
        message = f"Hello {user.first_name}!\n\nPlease confirm your email address to change your account password.\n\nRegards,\nThe Django Team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        # Send email confirmation link
        current_site = get_current_site(request)
        email_subject = "Change Password"
        message2 = render_to_string('base/reset_password.html', {
        'name': user.first_name,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [user.email],
        )
        email.send()
        messages.success(request, "Please check your email to reset your account password.")



    return render(request, 'base/get_email.html')

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        if request.method == 'POST':
            if request.POST.get('password1') != request.POST.get('password2'):
                messages.error(request, 'Passwords do not match')
                return redirect('reset-password')
            else:
                print('pass :', request.POST.get('password1'))
                myuser.set_password(request.POST.get('password1'))
                myuser.save()
                login(request, myuser)
                messages.success(request, 'Your password has been changed successfully')
                return redirect('login')
    else:
        print('Something went wrong')
    
    return render(request, 'base/get_passwords.html')


