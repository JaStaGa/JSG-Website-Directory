import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage
from .forms import CreateProfileForm, CreateStatusMessageForm


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


class CreateStatusMessageView(CreateView):
    ''' Creation of new status message 4 profiles '''
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs):
        ''' Adds profile to context, using pk '''
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        context['profile'] = profile
        return context

    def form_valid(self, form):
        ''' Links status message to correct profile '''
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        ''' Redirect user url after creation '''
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    

def home(request):
    return render(request, 'directory/base.html')