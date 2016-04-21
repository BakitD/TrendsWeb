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
			trends_obj = Trend.objects.filter(place_id=city.id)
			if not trends_obj: continue
			trends = []
			for t in trends_obj:
				if t.volume: trends.append((t.name, int(t.volume)))
				else: trends.append((t.name, t.volume))
			citytrends.append({'city' : city.name, 'city_tag' : city.name.replace(' ', '_'),\
				'trends' : sorted(trends, key=itemgetter(1), reverse=True)})
			if city.name == 'Santo Domingo': print citytrends
		return citytrends




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

