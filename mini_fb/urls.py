from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import CreateStatusMessageView, ShowAllProfilesView, ShowProfilePageView, CreateProfileView
from django.http import HttpResponse
from mini_fb import views




urlpatterns = [
    path('all_profiles/', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name="show_profile"),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    path('home', views.home, name='home'),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)