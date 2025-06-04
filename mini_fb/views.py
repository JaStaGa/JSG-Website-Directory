import random
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage, Image, StatusImage
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
        '''Links status message to profile and handles optional image upload'''
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = profile
        response = super().form_valid(form)  # Save status message first
        
        # Handle uploaded image if present
        image_file = self.request.FILES.get('image_file')
        if image_file:
            img = Image.objects.create(profile=profile, image_file=image_file, caption='')
            StatusImage.objects.create(image=img, status_message=form.instance)
        
        return response

    def get_success_url(self):
        ''' Redirect user url after creation '''
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    

def home(request):
    return render(request, 'directory/base.html')