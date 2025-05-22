# file hw/urls.py

from django.urls import path
from django.conf import settings
from . import views

# url patterns specific to the hw app:

urlpatterns = [
    path(r'', views.home_page, name="home_page"),
    #path(r'', views.home, name="home"),

]

