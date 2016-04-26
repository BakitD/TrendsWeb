from django.contrib import admin

from .models import Place, Trend, Placetype, Layer

admin.site.register(Layer)

admin.site.register(Place)

admin.site.register(Trend)

admin.site.register(Placetype)
