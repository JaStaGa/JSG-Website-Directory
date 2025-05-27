from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import ShowAllProfilesView, ShowProfilePageView


urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name="show_profile")
]
