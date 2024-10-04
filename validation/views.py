from django.shortcuts import render,redirect ,HttpResponse
from . models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def user_login(request):
   if request.method=='POST':
    username=request.POST['username']
    password=request.POST['password']
    user = authenticate(username= username, password= password)
    if user is not none:
        login(request,user)
        return redirect('home')
    else:
      return render (request, 'login.html',{'error':'invalid username or password'})
   else:
      return render(request,'login.html')





def register(request):
  if request.method=='POST':
   username=request.POST['username']
   email=request.POST['email']
   password=request.POST['password']
   firstname=request.POST['firstname']
   lastname=request.POST['lastname']

   hashed_password=make_password(password)
   user =user.objects.create(username=username, email=email, password=password, firstname=firstname,lastname=lastname )


   return redirect('login')
  else:
    return render(request,'register.html')
  
 
   

def user_logout(request):
   logout(request)
   return redirect ('login')
@login_required
def profile(request):
   User = request.user
   return render(request, 'profile.html',{'user': User})