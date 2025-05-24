# restaurants/views.py

import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

import time


def main(request):
    return render(request, 'restaurants/main.html')
                  
def order(request):
    return render(request, 'restaurants/order.html')

def confirmation(request):

    selected_items = []
    item_names = {
        "onigiri": "Brock's Onigiri $40",
        "apple": "Ryuk's Apple $15",
        "ramen": "Naruto's Ramen $60",
        "drumstick": "Luffy's Drumsticks $200",
        "special": "Eren's Spinal Fluid $15"
    }
    for item in item_names:
        if item in request.POST:
            selected_items.append(item_names[item])


    if request.POST:

        name = request.POST['name']
        phone = request.POST["phone"]
        email = request.POST["email"]
        special_instructions = request.POST["special_instructions"]

        context = {
            'time': time.ctime(),
            'selected_items': selected_items,
            'name': name,
            'phone': phone,
            'email': email,
            'special_instructions': special_instructions,
        }


    return render(request, 'restaurants/confirmation.html', context)