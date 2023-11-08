from django.forms import ModelForm
from .models import Room, User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import forms


class CustomUserCreationForm(forms.UserCreationForm):

    class Meta:
        model = User
        fields = ("email",'username')

class RoomForm(ModelForm):
    class Meta:
        model = Room
        exclude = ('host', 'participants', 'topic')

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','username', 'email', 'bio']



class DpForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar',]


