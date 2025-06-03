from django.db import models
from django.urls import reverse


class Profile(models.Model):
    '''Model for user profile'''

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=254, unique=True)
    image_file = models.ImageField(blank=True)

    def __str__(self):
        '''Returns string (full name) for profile'''
        return f'{self.first_name} {self.last_name}'
    
    # Accessor method to get all status messages for this profile, ordered by timestamp (most recent first)
    def get_status_messages(self):
        '''Returns all status messages for a profile in descending order'''
        return self.statusmessage_set.all().order_by('-timestamp')
    
    def get_absolute_url(self):
        '''Returns url to view a profile'''
        return reverse('show_profile', kwargs={'pk': self.pk})
    

class StatusMessage(models.Model):
    '''Model for status messages of a profile'''

    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image_file = models.ImageField(blank=True)


    def __str__(self):
        '''Returns string for status message (name, time, preview)'''
        return f'{self.profile.first_name} {self.profile.last_name} @ {self.timestamp}: {self.message[:30]}'


class Image(models.Model):
    '''Model for uploaded images'''

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image_file = models.ImageField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField()


    