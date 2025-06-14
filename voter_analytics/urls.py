from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from django.http import HttpResponse
from mini_fb import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    # 8-2-1
    path(r'', views.VoterListView.as_view(), name='base'),
    path(r'voters', views.VoterListView.as_view(), name='voters'),
    path(r'voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)