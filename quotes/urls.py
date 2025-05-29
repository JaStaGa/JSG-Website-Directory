# file quotes/urls.py

from django.conf.urls.static import static    ## add for static files
from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.quote, name='quotes'),
    path('quotes/', views.quote, name='quotes'),
    path('show_all/', views.show_all, name='show_all'),
    path('about/', views.about, name='about'),
    path('home/', views.home, name='home'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
