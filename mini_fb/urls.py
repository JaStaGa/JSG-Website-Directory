from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import CreateStatusMessageView, ShowAllProfilesView, ShowProfilePageView, CreateProfileView, UpdateProfileView, DeleteStatusMessageView, UpdateStatusMessageView, AddFriendView, ShowFriendSuggestionsView
from django.http import HttpResponse
from mini_fb import views




urlpatterns = [
    path('all_profiles/', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name="show_profile"),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
    path('profile/<int:pk>/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/friend_suggestions/', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('home', views.home, name='home'),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)