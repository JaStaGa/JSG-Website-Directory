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
    
    def get_friends(self):
        '''Returns list of friend's profiles'''
        sent = Friend.objects.filter(profile1=self)
        received = Friend.objects.filter(profile2=self)
        return [f.profile2 for f in sent] + [f.profile1 for f in received]
    
    def add_friend(self, other):
        '''Adds other as friend of self'''
        # print("ATTEMPTING TO ADD FRIEND")
        if self == other:
            # print("CAN NOT FRIEND YOURSELF")
            return
        
        # Check if a Friend object already exists in either direction
        if Friend.objects.filter(profile1=self, profile2=other).exists() or Friend.objects.filter(profile1=other, profile2=self).exists():
            # print("NO NEW FRIENDSHIP - ALREADY FRIENDS")
            return  # already friends    
        
        Friend.objects.create(profile1=self, profile2=other)

    def get_friend_suggestions(self):
        """Return list of Profiles that are not already friends and not self."""
        all_profiles = set(Profile.objects.exclude(pk=self.pk))
        current_friends = set(self.get_friends())
        return list(all_profiles - current_friends)
    

class StatusMessage(models.Model):
    '''Model for status messages of a profile'''

    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        '''Returns string for status message (name, time, preview)'''
        return f'{self.profile.first_name} {self.profile.last_name} @ {self.timestamp}: {self.message[:30]}'
    
    def get_images(self):
        '''Returns images related to this StatusMessage via StatusImage'''
        return Image.objects.filter(statusimage__status_message=self)


class Image(models.Model):
    '''Model for uploaded images'''

    image_file = models.ImageField(upload_to='profile_images/')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='images')
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=255, blank=True)


class StatusImage(models.Model):
    '''Model for uploaded images'''

    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Image {self.image.id} linked to StatusMessage {self.status_message.id}"
    

class Friend(models.Model):
    '''Model for friend connections'''

    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends_sent')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends_received')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}"
    