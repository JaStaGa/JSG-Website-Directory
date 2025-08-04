# file hw/views.property

import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

import time


quotes_list = [
    "Real G's move in silence like lasagna",
    "Weezy f. Baby and the f is for phenomenal",
    "We gonna be alright if we put Drake on every hook",
    "Most of yall don't get the picture unless the flash is on",
    "And when I was five my favorite movie was The Gremlins",
    "Love me or hate me, i swear it won't make or break me",
    "I tried to pay attention, but attention paid me",
    "What goes around comes around like a hool-a-hoop",
    "Prepared for the worst,but still praying for the best",
    "Your gonna need a spaceshuttle or a ladder that's forever to get on my level",
    "Take them shoes of your teeth and quit running your mouth",
    "I call them April babies cuz they fools",
    "Life is a beach and i am juss playing in the sand",
    "Be good, or be good at it",
    "Everybody Dies But Not Everybody Lives",
    "Drag my name through the mud, i come out clean",
    "I do what I do, and you do what you can do about it",
]

images_list = [
    # User-provided
    "https://static.wikia.nocookie.net/hip-hop-music/images/2/2f/Lil_Wayne.png/revision/latest?cb=20140916154841",
    "https://hips.hearstapps.com/hmg-prod/images/lil_wayne_photo_by_ray_tamarra_getty_images_entertainment_getty_56680625.jpg",
    "https://vegnews.com/media/W1siZiIsIjQ3MDk3L0xpbC1XYXluZS5qcGciXSxbInAiLCJjcm9wX3Jlc2l6ZWQiLCI3NjF4NzYxKzI0OSswIiwiOTQ2eDk0Nl4iLHsiZm9ybWF0IjoianBnIn1dLFsicCIsIm9wdGltaXplIl1d/Lil-Wayne.jpg?sha=ac80881601bc6090",
    "https://upload.wikimedia.org/wikipedia/commons/a/a6/Lil_Wayne_%2823513397583%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/55/Lil_Wayne_%2823513397583%29.png",
    "https://upload.wikimedia.org/wikipedia/commons/d/d9/2011%E5%B9%B47%E6%9C%8816%E6%97%A5_%E3%83%8B%E3%83%BC%E3%83%AB%E3%83%96%E3%83%AC%E3%82%A4%E3%83%87%E3%83%AB%E3%83%BB%E3%82%A2%E3%83%AA%E3%83%BC%E3%83%8A.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/e/e0/Lil_Wayne.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/5d/Lil_Wayne_Camp_Flog_Gnaw_2012.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/5a/Lil_Wayne_cropped.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/12/Lil_Wayne_Feb._2020.jpg",

]


def quote(request):
    quote = random.choice(quotes_list)
    image = random.choice(images_list)
    return render(request, 'quotes/quote.html', {'quote': quote, 'image': image})

def show_all(request):
    image = random.choice(images_list)
    return render(request, 'quotes/show_all.html', {'quotes': quotes_list, 'image': image})

def about(request):
    return render(request, 'quotes/about.html')

def home(request):
    return render(request, 'directory/base.html')