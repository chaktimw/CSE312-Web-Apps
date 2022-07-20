from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import profile

class registerForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'password1', 'password2' ]

class profileSigForm(forms.ModelForm):
	class Meta:
		model = profile
		fields = ['signature']

class profileUpdateForm(forms.ModelForm):
	class Meta:
		model = profile
		fields = ['image']