from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Worker,Customer

class userUpdate(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','email']

class userUpdateAdd(forms.ModelForm):
    class Meta:
        model=Customer
        fields=['phone','address']

class customerForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model=User
        fields=['first_name','last_name','username','email','password']

class customerAddForm(forms.ModelForm):
    class Meta():
        model=Customer
        fields=['phone','address']

class workerForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model=User
        fields=['username','email','password']

class workerAddForm(forms.ModelForm):
    class Meta():
        model=Worker
        fields=['name','phone','worker_type','salary','img']
           