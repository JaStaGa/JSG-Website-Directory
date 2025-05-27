import random
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

import time

# Create your views here.
def base(request):

    response_text = f'''
    <html>
    <h1>Hello World!</h1>
    The current time is {time.ctime()}.
    </html>
    '''
 
    return HttpResponse(response_text)