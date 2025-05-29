from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import ShowAllProfilesView, ShowProfilePageView
from django.http import HttpResponse




urlpatterns = [
    path('all_profiles/', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', S