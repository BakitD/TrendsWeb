# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from djgeojson.fields import PointField
from django.db import models
from operator import itemgetter

from datetime import datetime, timedelta

from .settings import DATETIME_FORMAT, TREND_STORE_DAYS, TREND_UPDATE_FREQ, DATE_FORMAT, USER_DATE_FORMAT

class TrendModel(models.Model):
	geom = PointField()
	name = models.TextField()

	@property
	def popupContent(self):
		return '{}'.format(self.name.encode('utf8'))

class Place(models.Model):
	name = models.CharField(unique=True, max_length=32)
	woeid = models.CharField(unique=True, max_length=16)
	longitude = models.CharField(max_length=32)
	latitude = models.CharField(max_length=32)
	parent_id = models.CharField(max_length=16, blank=True, null=True)
	dtime = models.DateTimeField()
	placetype = models.ForeignKey('Placetype', models.DO_NOTHING)

	def __unicode__(self):
		return u'{0} ({1})'.format(self.name, self.woeid)

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
		trends = []
		for city in cities:
			dtrange = [city.dtime.date(), city.dtime]
			trends = Trend.objects.filter(place_id=city.id, dtime__range=dtrange).values('name', 'volume')
			if not trends: continue
			citytrends.append({'place' : city.name, 'place_tag' : city.woeid, 'woeid' : city.woeid,
				'trends' : sorted(trends, key=city.sort_place, reverse=True)})
		return citytrends


	@staticmethod
	def get_countrytrends(woeid):
		country = Place.objects.filter(woeid=woeid).first()
		trends = Trend.objects.values('name', 'volume').filter(place_id=country.id,
					dtime__range=[country.dtime.date(), country.dtime])
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
	name = models.CharField(max_length=255)
	volume = models.CharField(max_length=32, blank=True, null=True)
	place = models.ForeignKey(Place, models.DO_NOTHING)
	dtime = models.DateTimeField()

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
			trends = Trend.objects.filter(place_id=place.id,
				dtime__range=[end_date.date(), end_date]).values('name', 'volume')
			week_trends.append({'datetime':end_date.strftime(USER_DATE_FORMAT), 'day_id' : days_counter,
					'trends' : sorted(trends, key=place.sort_place, reverse=True)})
			end_date = end_date - timedelta(days=1)
			days_counter += 1
		return week_trends






