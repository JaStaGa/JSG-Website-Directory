from django import forms
from .models import Profile, StatusMessage 

class CreateProfileForm(forms.ModelForm):
    '''Class for profile creation form'''

    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    city = forms.CharField(label="City", required=True)
    email_address = forms.EmailField(label="Email Address", required=True)
    profile_image_url = forms.URLField(label="Profile Image URL", required=True)

    class Meta:
        '''MetaData for CreateProfileForm'''
        
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'profile_image_url']

class CreateStatusMessageForm(forms.ModelForm):
    '''Class for message creation form'''

    class Meta:
        model = StatusMessage
        fields = ['message']  