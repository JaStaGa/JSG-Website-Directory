import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse


import time

def base(request):
    return render(request, 'directory/base.html')

def quotes(request):
    return render(request, 'quotes/quote.html')

def restaurants(request):
    return render(request, 'restaurants/main.html')

def mini_fb(request):
    return render(request, 'mini_fb/base.html')

def voter_analytics(request):
    return render(request, 'voter_analytics/voter_list.html')