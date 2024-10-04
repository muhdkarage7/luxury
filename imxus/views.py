from django.shortcuts import render,HttpResponse
from .models import *

# Create your views here.

def index(request):
    return render(request, 'index.html')

def contact_us (request):
    if request.method=='POST':
     firstname=request.POST.get('firstname')
     lastname=request.POST.get('lastname')
     email=request.POST.get('email')
     country=request.POST.get('country')
     subject=request.POST.get('subject')
