from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from django.http import HttpResponse
from mini_fb import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView



urlpatterns = [
    path('home', views.home, name='home'),
    path('all_profiles/', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name="show_profile"),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
    # 7-2-1
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('logout_confirmation/', TemplateView.as_view(template_name='mini_fb/logged_out.html'), name='logout_confirmation'),
    # 7-2-5
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path('status/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
    path('profile/friend_suggestions/', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/news_feed', ShowNewsFeedView.as_view(), name='show_news_feed'),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)