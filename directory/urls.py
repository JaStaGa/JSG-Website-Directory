from django.conf.urls.static import static    ## add for static files
from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.base, name='base'),
    path('quotes/', views.quotes, name='quotes'),
    path('restaurants/', views.r