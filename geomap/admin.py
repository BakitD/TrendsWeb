from django.contrib import admin

from .models import Place, Trend, Placetype, Layer

class PlaceAdmin(admin.ModelAdmin):
	search_fields = ('name',)


class TrendAdmin(admin.ModelAdmin):
	search_fields = ('name',)


admin.site.register(Layer)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Trend, TrendAdmin)
admin.site.register(Placetype)
