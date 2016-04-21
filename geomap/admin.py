from django.contrib import admin

from .models import Place, Trend, Placetype

admin.site.register(Place)

admin.site.register(Trend)

admin.site.register(Placetype)
