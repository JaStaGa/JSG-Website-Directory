# file hw/urls.py

from django.conf.urls.static import static    ## add for static files
from django.urls import path
from django.conf import settings
from . import views

# url patterns specific to the hw app:

urlpatterns = [
    path(r'', views.home_page, name="home"),
    #path(r'', views.home, name="home"),
    path(r'about', views.about, name="about"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
