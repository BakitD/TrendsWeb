from django.db.models import signals
from django.dispatch import receiver

from django.core.cache import cache
from .models import Place, Layer
from .settings import CACHE_LAYER_NAME

@receiver(signals.post_save, sender=Place)
def post_layer_update(sender, instance, created, **kwargs):
	if not created:
		layer_dict = cache.get(CACHE_LAYER_NAME) or {}
		layers = Layer.objects.all()
		for layer in layers:
			woeids = tuple(Place.objects.filter(layer_id=layer.id).values_list('woeid', flat=True))
			layer_dict[layer.scale] = woeids
		cache.set(CACHE_LAYER_NAME, layer_dict, timeout=None)
	print cache.get(CACHE_LAYER_NAME)
