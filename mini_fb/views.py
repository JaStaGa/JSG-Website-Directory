import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView
from django.views.generic import DetailView
from .models import Profile


import time

# Create your views here.
class ShowAllProfilesView(ListView):
    model = Profile
    template_name="mini_fb/show_all_profiles.html"
    context_object_name="profiles"

class ShowProfilePageView(DetailView):
    model = Profile
    template_name="mini_fb/show_profile.html"
