# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models
from operator import itemgetter

from datetime import datetime, timedelta
from .settings import DATETIME_FORMAT, TREND_STORE_DAYS, TREND_UPDATE_FREQ, DATE_FORMAT, USER_DATE_FORMAT


class GeoTrend(models.Model):
	dtime = models.DateTimeField()
	volume = models.IntegerField(blank=True, null=True)
	trend = models.ForeignKey('Trend', models.DO_NOTHING)
	place = models.ForeignKey('Place', models.DO_NOTHING)

	class Meta:
		managed = False
		db_table = 'geotrend'
		unique_together = (('place', 'trend', 'dtime'),)

	def __unicode__(self):
		return u'trend_id: {0}, place_id: {0}, volume: {3}'.format(self.trend, self.place, self.volume)

class Layer(models.Model):
	name = models.CharField(unique=True, max_length=64)
	scale = models.IntegerField(unique=True)

	class Meta:
		managed = False
		db_table = 'layer'

	def __unicode__(self):
		return u'{0}, (scale {1})'.format(self.name, self.scale)


class Place(models.Model):
	name = models.CharField(max_length=32)
	woeid = models.CharField(unique=True, max_length=16)
	longitude = models.CharField(max_length=32)
	latitude = models.CharField(max_length=32)
	dtime = models.DateTimeField()
	parent_id = models.CharField(max_length=16, blank=True, null=True)
	placetype = models.ForeignKey('Placetype', models.DO_NOTHING)
	layer = models.ForeignKey(Layer, models.DO_NOTHING, blank=True, null=True)

	def __unicode__(self):
		return u'{0} ({1})'.format(self.name, self.woeid, self.dtime)

	class Meta:
		managed = False
		db_table = 'place'

	@staticmethod
	def get_countries():
		cid = Placetype.objects.filter(name='country').first().id
		countries = Place.objects.filter(placetype_id=cid).order_by('name')
		return [{'name' : country.name, 'woeid' : country.woeid} for country in countries]


	@staticmethod
	def get_citytrends(woeid):
		citytrends = []
		country = Place.objects.filter(woeid=woeid).first()
		cities = Place.objects.filter(parent_id=woeid).order_by('name')
		for city in cities:
			geotrends = GeoTrend.objects.filter(place_id=city.id, 
				dtime__range=[city.dtime.date(), city.dtime])#values('trend_id', 'volume')
			if not geotrends: continue
			trends = []
			for geotrend in geotrends:
				trends.append({'name': Trend.objects.filter(id=geotrend.trend_id).first().name,
						'volume' : geotrend.volume})
			citytrends.append({'place' : city.name, 'place_tag' : city.woeid, 'woeid' : city.woeid,
				'trends' : sorted(trends, key=city.sort_place, reverse=True)})
		return citytrends


	@staticmethod
	def get_countrytrends(woeid):
		country = Place.objects.filter(woeid=woeid).first()
		geotrends = GeoTrend.objects.filter(place_id=country.id,
					dtime__range=[country.dtime.date(), country.dtime])
		trends = []
		for geotrend in geotrends:
			trends.append({'name': Trend.objects.filter(id=geotrend.trend_id).first().name,
					'volume' : geotrend.volume})
		return {'place' : country.name, 'place_tag' : country.woeid, 'woeid' : country.woeid,
				'trends' : sorted(trends, key=country.sort_place, reverse=True)}

	def sort_place(self, element):
		value = element.get('volume') or 0
		return int(value)



class Placetype(models.Model):
	name = models.CharField(unique=True, max_length=16)

	class Meta:
		managed = False
		db_table = 'placetype'

	def __unicode__(self):
		return u'{0}'.format(self.name)


class Trend(models.Model):
	name = models.CharField(unique=True, max_length=255)

	class Meta:
		managed = False
		db_table = 'trend'


	def __unicode__(self):
		return u'{0}'.format(self.name)


	@staticmethod
	def get_weektrends(woeid):
		place = Place.objects.filter(woeid=woeid).first()
		end_date = place.dtime
		days_counter = 0
		week_trends = []
		while days_counter < TREND_STORE_DAYS:
			geotrends = GeoTrend.objects.filter(place_id=place.id, dtime__range=[end_date.date(), end_date])
			trends = []
			for geotrend in geotrends:
				trends.append({'name': Trend.objects.filter(id=geotrend.trend_id).first().name,
					'volume' : geotrend.volume})
			week_trends.append({'datetime':end_date.strftime(USER_DATE_FORMAT), 'day_id' : days_counter,
					'trends' : sorted(trends, key=place.sort_place, reverse=True)})
			end_date = end_date - timedelta(days=1)
			days_counter += 1
		return week_trends


