# file hw/views.property

import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

import time


quotes_list = [
    "Real G's move in silence like lasagna",
    "Weezy f. Baby and the f is for phenomenal",
    "We gonna be alright if we put Drake on every hook",
    "Most of yall don’t get the picture unless the flash is on",
]

images_list = [
    "https://static.wikia.nocookie.net/hip-hop-music/images/2/2f/Lil_Wayne.png/revision/latest?cb=20140916154841",
    "https://hips.hearstapps.com/hmg-prod/images/lil_wayne_photo_by_ray_tamarra_getty_images_entertainment_getty_56680625.jpg",
    "https://vegnews.com/media/W1siZiIsIjQ3MDk3L0xpbC1XYXluZS5qcGciXSxbInAiLCJjcm9wX3Jlc2l6ZWQiLCI3NjF4NzYxKzI0OSswIiwiOTQ2eDk0Nl4iLHsiZm9ybWF0IjoianBnIn1dLFsicCIsIm9wdGltaXplIl1d/Lil-Wayne.jpg?sha=ac80881601bc6090",
    ]

def quote(request):
    quote = random.choice(quotes_list)
    image = random.choice(images_list)
    return render(request, 'quotes/quote.html', {'quote': quote, 'image': image})

def show_all(request):
    return render(request, 'quotes/show_all.html', {'quotes': quotes_list, 'images': images_list})

def about(request):
    return render(request, 'quotes/about.html')
