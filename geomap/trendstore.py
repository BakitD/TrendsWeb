# This module implements access to trends through
# redis and cache to use in ajax functions and
# hides work with layers.
# Trends are stored in redis database. To avoid
# treatment to SQL database cache is used.
# Cache stores dictionary where key is layers scale
# and value is tuple of woeids. This structure updates
# every time when administrator adds or delete place from
# layer. Therefore post_layer_update is defined here.
# Class TrendStore implements access to redis database.

from django_redis import get_redis_connection
from django.core.cache import cache
from django.db.models import signals
from django.dispatch import receiver

from .settings import CACHE_LAYER_NAME, REDIS_LOCATION_KEY_NAME
from .models import Place, Layer

import json

redis = get_redis_connection('default')

class TrendStore:
	def __init__(self):
		self.trends = {}
		#self.update_trends()

	def update_trends(self):
		redisTrends = redis.get('geomap')
		if redisTrends:	self.trends = json.loads(redisTrends)

	def get_trends_by_layer(self, scale):
		self.update_trends()
		woeids = cache.get(CACHE_LAYER_NAME) or ()
		if woeids: woeids = woeids.get(scale)
		#if not self.trends: self.update_trends()
		return {key : self.trends[key] for key in self.trends.keys() if key in woeids}		

	def get_places(self, scale, swLat, swLng, neLat, neLng):
		woeids = cache.get(CACHE_LAYER_NAME) or ()
		if woeids: woeids = woeids.get(scale) or ()
		trends = {}
		#if not self.trends: self.update_trends()
		for woeid in woeids:
			try:
				value = self.trends.get(woeid)
				coordinates = value.get('coordinates')
				longitude = float(coordinates.get('longitude'))
				latitude = float(coordinates.get('latitude'))
				if (longitude > swLng and longitude < neLng and 
					latitude > swLat and latitude < neLat):
					trends[woeid] = self.trends[woeid]
			except Exception: pass
		return trends

	def get_scales(self):
		scales = cache.get(CACHE_LAYER_NAME) or {}
		return scales.keys()





# Definition of callback for action after signal
@receiver(signals.post_save, sender=Place)
def post_layer_update(sender, instance, created, **kwargs):
	if not created:
		layer_dict = cache.get(CACHE_LAYER_NAME) or {}
		layers = Layer.objects.all()
		for layer in layers:
			woeids = tuple(Place.objects.filter(layer_id=layer.id).values_list('woeid', flat=True))
			layer_dict[layer.scale] = woeids
		cache.set(CACHE_LAYER_NAME, layer_dict, timeout=None)


tStore = TrendStore()
