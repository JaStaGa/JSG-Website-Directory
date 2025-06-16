from django.contrib import admin
from .models import Attribute, Badge, BadgeLevel, Build

admin.site.register(Attribute)
admin.site.register(Badge)
admin.site.register(BadgeLevel)
admin.site.register(Build)