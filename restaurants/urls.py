from django.conf.urls.static import static    ## add for static files
from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('main/', views.main, name='main'),
    path('order/', views.order, name='order'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('home', views.home, name='home'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)