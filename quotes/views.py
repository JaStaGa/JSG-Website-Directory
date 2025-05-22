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
    "static/quotes/lil_wayne_1.jpeg",
    "static/quotes/lil-wayne-2.jpeg",
    "static/quotes/lil_wayne_3.jpeg",
    ]

def quote(request):
    quote = random.choice(quotes_list)
    image = random.choice(images_list)
    return render(request, 'quotes/quote.html', {'quote': quote, 'image': image})

def show_all(request):
    return render(request, 'quotes/show_all.html', {'quotes': quotes_list, 'images': images_list})

def about(request):
    return render(request, 'quotes/about.html')
