from django.db import models
from django.urls import reverse


class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=254, unique=True)
    profile_image_url = models.URLField(max_length=200, unique=True)

    def __str__(self):
        return f'{s