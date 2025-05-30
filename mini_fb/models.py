from django.db import models
from django.urls import reverse


class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=254, unique=True)
    profile_image_url = models.URLField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    # Accessor method to get all status messages for this profile, ordered by timestamp (most recent first)
    def get_status_messages(self):
        return self.statusmessage_set.all().order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    

class StatusMessage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.profile.first_name} {self.profile.last_name} @ {self.timestamp}: {self.message[:30]}'

