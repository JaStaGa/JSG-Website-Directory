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
    path('home', views.home, name='home'),  # back to home/directory
    # 8-2
    path('', views.base, name='voter_analytics_home'),    # app home 
    path('voters', views.VoterListView.as_view(), name='voters'),  # voter list
    # 8-2
    path('voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'), # specific voter
    # 8-3
    path('graphs', views.VoterGraphView.as_view(), name='graphs'),  # voter graphs
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)