# restaurants/views.py

import random
import time
from datetime import datetime, timedelta
import pytz

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def main(request):
    return render(request, 'restaurants/main.html')

def order(request):
    return render(request, 'restaurants/order.html')

def confirmation(request):
    menu = {
        "soba_shop": ("Sanji's Soba Shop Special - $20", 20),
        "potato_pallie": ("Potato Pallie - $15", 15),
        "strawhat_special": ("Luffy's Meat On The Bone - $30", 30),
        "bigmom_cake": ("Big Mom's Wedding Cake - $35", 35),
        "sentimental_mom": ("Sentimental Meal For Mom - $18", 18),
        "bento_luffy": ("Bento For Luffy - $22", 22)
    }
    selected_items = []
    total = 0
    for item in menu:
        if item in request.POST:
            name, price = menu[item]
            selected_items.append(name)
            total += price


    if request.POST:
        name = request.POST['name']
        phone = request.POST["phone"]
        email = request.POST["email"]
        special_instructions = request.POST["special_instructions"]

        # random time in EST (between 30 and 60 minutes from now)
        est = pytz.timezone('US/Eastern')
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        random_minutes = random.randint(30, 60)
        ready_time = now_utc + timedelta(minutes=random_minutes)
        ready_time_est = ready_time.astimezone(est)
        formatted_time = ready_time_est.strftime('%I:%M %p')  # 12hr format with AM/PM

        context = {
            'time': formatted_time,
            'selected_items': selected_items,
            'name': name,
            'phone': phone,
            'email': email,
            'special_instructions': special_instructions,
            'total': total,
        }

        return render(request, 'restaurants/confirmation.html', context)

def home(request):
    return render(request, 'directory/base.html')