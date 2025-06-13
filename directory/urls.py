from django.conf.urls.static import static    ## add for static files
from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.base, name='base'),
    path('quotes/', views.quotes, name='quotes'),
    path('restaurants/', views.restaurants, name='restaurants'),
    path('mini_fb/', views.mini_fb, name='mini_fb'),
    path('voter_analytics/', views.voter_analytics, name='voter_analytics'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
