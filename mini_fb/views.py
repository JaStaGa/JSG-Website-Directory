import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile
from .forms import CreateProfileForm


import time

class ShowAllProfilesView(ListView):
    '''Class to view all profiles'''

    model = Profile
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"


class ShowProfilePageView(DetailView):
    '''Class to view a single profile'''
    model = Profile
    template_name="mini_fb/show_profile.html"


class CreateProfileView(CreateView):
    '''Class to create a profile'''
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'