from django.contrib import admin

from .models import Place, Trend, Placetype, Layer, Clusters, Word, TrendWord

class PlaceAdmin(admin.ModelAdmin):
	search_fields = ('name',)


class TrendAdmin(admin.ModelAdmin):
	search_fields = ('name',)

class ClustersWord(admin.TabularInline):
	model = Word

class ClustersAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	inlines = [ClustersWord,]

class WordAdmin(admin.ModelAdmin):
	search_fields = ('name',)


class TrendWordAdmin(admin.ModelAdmin):
	search_fields = ('trend_id', 'word_id',)

admin.site.register(Layer)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Trend, TrendAdmin)
admin.site.register(Placetype)
admin.site.register(Word, WordAdmin)
admin.site.register(Clusters, ClustersAdmin)
admin.site.register(TrendWord)
