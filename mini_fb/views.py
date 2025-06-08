import random
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView, UpdateView
from .models import Profile, StatusMessage, Image, StatusImage, Friend
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django.contrib.auth import login 
import time

class ShowAllProfilesView(ListView):
    '''Class to view all profiles'''

    model = Profile
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"

    def dispatch(self, request, *args, **kwargs):
        '''Override the dispatch method to add debugging information.'''

        if request.user.is_authenticated:
            print(f'ShowAllProfilesView.dispatch(): request.user={request.user}')
        else:
            print(f'ShowAllProfilesView.dispatch(): not logged in.')

        return super().dispatch(request, *args, **kwargs)



class ShowProfilePageView(DetailView):
    '''Class to view a single profile'''
    model = Profile
    template_name="mini_fb/show_profile.html"


# 7-1-4
class CreateProfileView(LoginRequiredMixin, CreateView):
    '''View to create a new Profile instance.'''

    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"

    def get_login_url(self) -> str:
        '''return the URL required for login'''
        return reverse('login') 
    
    def form_valid(self, form):
        '''
        Handle the form submission to create a new Profile object.
        '''
        print(f'CreateProfileView: form.cleaned_data={form.cleaned_data}')

        # find the logged in user
        user = self.request.user
        print(f"CreateProfileView user={user} profile.user={user}")

        # attach user to form instance (Profile object):
        form.instance.user = user

        return super().form_valid(form)
    

# 7-1-4
class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    ''' Creation of new status message 4 profiles '''
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs):
        ''' Adds profile to context, using pk '''
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''Links status message to profile and handles multiple image uploads'''
        profile = Profile.objects.get(user=self.request.user)
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
        profile = Profile.objects.get(user=self.request.user)
        return reverse('show_profile', kwargs={'pk': profile.pk})       

def home(request):
    return render(request, 'directory/base.html')
# 7-1-4
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''For updating profile'''
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse_lazy('show_profile', kwargs={'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

# 7-1-4
class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status'

    def get_success_url(self):
        profile = self.object.profile
        return reverse_lazy('show_profile', kwargs={'pk': profile.pk})
    
# 7-1-4
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    model = StatusMessage
    fields = ['message']
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status'

    def get_success_url(self):
        profile = self.object.profile
        return reverse_lazy('show_profile', kwargs={'pk': profile.pk})
    
# 7-1-4
class AddFriendView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        # Raise exception if object doesnt exist
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])

        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['friend_suggestions'] = profile.get_friend_suggestions()
        return context
    
    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)
    
class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['news_feed'] = profile.get_news_feed()
        return context
    
    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)





class RegistrationView(CreateView):
    '''
    show/process form for account registration
    '''

    template_name = 'mini_fb/register.html'
    form_class = UserCreationForm
    model = User


class UserRegistrationView(CreateView):
    '''A view to show/process the registration form to create a new User.'''

    template_name = 'mini_fb/register.html'
    form_class = UserCreationForm
    model = User
    
    def get_success_url(self):
        '''The URL to redirect to after creating a new User.'''
        return reverse('login')