from django import forms
from .models import Profile, StatusMessage, Image 

class CreateProfileForm(forms.ModelForm):
    '''Class for profile creation form'''

    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    city = forms.CharField(label="City", required=True)
    email_address = forms.EmailField(label="Email Address", required=True)
    image_file = forms.ImageField

    class Meta:
        '''MetaData for CreateProfileForm'''
        
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'image_file']

class CreateStatusMessageForm(forms.ModelForm):
    '''Class for message creation form'''
    image_file = forms.ImageField(required=False)

    class Meta:
        model = StatusMessage
        fields = ['message']  