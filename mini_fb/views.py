import random
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView, UpdateView
from .models import Profile, StatusMessage, Image, StatusImage
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm


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
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def form_valid(self, form):
        # Save the profile 
        response = super().form_valid(form)

        # Debug log — check what’s in request.FILES
        print("FILES:", self.request.FILES)

        # Handle image upload 
        image_file = self.request.FILES.get('image_file')
        if image_file:
            # Create Image object linked to new profile
            Image.objects.create(profile=self.object, image_file=image_file, caption='')

        return response
    
    def get_success_url(self):
        # Redirect to profile detail page after creation
        return reverse('show_profile', kwargs={'pk': self.object.pk})


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
        '''Links status message to profile and handles multiple image uploads'''
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = profile
        
        # Save the status message
        sm = form.save()

        # Get uploaded files
        files = self.request.FILES.getlist('files')
        print("FILES:", files)

        for f in files:
            print("Processing file:", f)
            # Create the Image object
            img = Image.objects.create(profile=profile, image_file=f, caption="")  # You can enhance with a real caption
            # Create the StatusImage link
            StatusImage.objects.create(image=img, status_message=sm)

        return redirect(self.get_success_url())

    def get_success_url(self):
        ''' Redirect user url after creation '''
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    

def home(request):
    return render(request, 'directory/base.html')

class UpdateProfileView(UpdateView):
    '''For updating profile'''
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})


class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status'

    def get_success_url(self):
        profile = self.object.profile
        return reverse_lazy('show_profile', kwargs={'pk': profile.pk})
    

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    fields = ['message']
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status'

    def get_success_url(self):
        profile = self.object.profile
        return reverse_lazy('show_profile', kwargs={'pk': profile.pk})
