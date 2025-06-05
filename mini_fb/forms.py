from django import forms
from .models import Profile, StatusMessage, Image 

class CreateProfileForm(forms.ModelForm):
    '''Class for profile creation form'''

    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    city = forms.CharField(label="City", required=True)
    email_address = forms.EmailField(label="Email Address", required=True)
    image_file = forms.ImageField(required=False)

    class Meta:
        '''MetaData for CreateProfileForm'''
        
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'image_file']

class CreateStatusMessageForm(forms.ModelForm):
    '''Class for message creation form'''

    class Meta:
        model = StatusMessage
        fields = ['message']  


class UpdateProfileForm(forms.ModelForm):
    '''Form for updating a Profile (without changing first or last name)'''

    class Meta:
        model = Profile
        fields = ['city', 'email_address', 'image_file']