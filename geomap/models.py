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

import time
from datetime import datetime, timedelta
from .settings import DATETIME_FORMAT, TREND_STORE_DAYS, TREND_SEARCH_LIMIT, \
		TREND_UPDATE_FREQ, DATE_FORMAT, USER_DATE_FORMAT
from collections import OrderedDict


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
		return u'trend_id: {0}, place_id: {1}, volume: {2}'.format(self.trend, self.place, self.volume)


class Layer(models.Model):
	name = models.CharField(unique=True, max_length=64)
	scale = models.IntegerField(unique=True)

	class Meta:
		managed = False
		db_table = 'layer'

	def __unicode__(self):
		return u'{0}, (scale {1})'.format(self.name, self.scale)


class Place(models.Model):
	name = models.CharField(max_length=64)
	woeid = models.CharField(unique=True, max_length=16)
	longitude = models.CharField(max_length=32)
	latitude = models.CharField(max_length=32)
	dtime = models.DateTimeField()
	parent_id = models.CharField(max_length=16, blank=True, null=True)
	placetype = models.ForeignKey('Placetype', models.DO_NOTHING)
	layer = models.ForeignKey(Layer, models.DO_NOTHING, blank=True, null=True)
	another_name = models.CharField(max_length=64, blank=True, null=True)

	def __unicode__(self):
		return u'{0} ({1}), ({2}, {3})'.format(self.name, self.another_name, self.woeid, self.dtime)

	class Meta:
		managed = False
		db_table = 'place'


	@staticmethod
	def get_places_for_trend(trendid, date):
		geotrends = GeoTrend.objects.filter(trend_id=trendid)
		places = {}
		for gt in geotrends:
			if gt.dtime.strftime(USER_DATE_FORMAT) == date:
				place = Place.objects.filter(id=gt.place_id).first()
				places[int(place.woeid)] = {'name':place.name, 'longitude':place.longitude,
						'latitude':place.latitude, 'dates' : []}
		try:
			if places.get(1): del places[1]
		except Exception: pass
		return places


	@staticmethod
	def get_countries():
		cid = Placetype.objects.filter(name='country').first().id
		countries = Place.objects.filter(placetype_id=cid).order_by('another_name')
		return [{'name' : country.name, 'another_name' : country.another_name,\
					 'woeid' : country.woeid} for country in countries]


	@staticmethod
	def get_citytrends(woeid):
		citytrends = []
		country = Place.objects.filter(woeid=woeid).first()
		cities = Place.objects.filter(parent_id=woeid).order_by('another_name')
		for city in cities:
			geotrends = GeoTrend.objects.filter(place_id=city.id, 
				dtime__range=[city.dtime.date(), city.dtime])#values('trend_id', 'volume')
			if not geotrends: continue
			trends = []
			for geotrend in geotrends:
				trends.append({'name': Trend.objects.filter(id=geotrend.trend_id).first().name,
						'volume' : geotrend.volume})
			citytrends.append({'place' : city.name, 'place_tag' : city.woeid, 'woeid' : city.woeid,
				'trends' : sorted(trends, key=city.sort_place, reverse=True), \
				'another_name' : city.another_name})
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
		return {'place' : country.name, 'another_name': country.another_name,'place_tag' : country.woeid, \
				'woeid' : country.woeid,\
				'trends' : sorted(trends, key=country.sort_place, reverse=True)}
	@staticmethod
	def get_worldwide():
		trends = []
		placetype = Placetype.objects.filter(name='worldwide').first()
		if placetype:
			worldwide = Place.objects.filter(placetype_id=placetype.id).first()
			geotrends = []
			if worldwide:
				geotrends = GeoTrend.objects.filter(place_id=worldwide.id,
					dtime__range=[worldwide.dtime.date(), worldwide.dtime])
			for geotrend in geotrends:
				trends.append({'name': Trend.objects.filter(id=geotrend.trend_id).first().name,
						'volume' : geotrend.volume, 'id':geotrend.trend_id})
		if not trends: result = []
		else:
			result = {'place' : worldwide.name, 'place_tag' : worldwide.woeid, 'woeid' : worldwide.woeid,
				'trends' : sorted(trends, key=worldwide.sort_place, reverse=True)}
		return result


	@staticmethod
	def get_trend_places(trendid):
		geotrends = GeoTrend.objects.filter(trend_id=trendid)#.order_by('dtime')
		worldwide = False
		result = {}
		places = Place.objects.all()
		for gt in geotrends:	
			dtime = gt.dtime.strftime(USER_DATE_FORMAT)
			if not result.get(dtime): result[dtime] = {}
			place = places.get(id=gt.place_id)
			if int(place.woeid) != 1:#and int(place.parent_id) != 1 and
				if int(place.parent_id) == 1: country = place
				else: country = places.get(woeid=place.parent_id)
				if not result[dtime].get(country.name):
					result[dtime][country.name] = { 'cities' : [], \
							'countrytagname' : country.name.replace(' ', ''),\
							'country_name':country.another_name}
				if int(place.parent_id) != 1:
					result[dtime][country.name]['cities'].append({'name':place.name,\
					'another_name':place.another_name,\
					'longitude':place.longitude,\
					'latitude':place.latitude, 'dtime':gt.dtime, 'volume':gt.volume})
			elif int(place.woeid) == 1:
				worldwide = True
			result[dtime]['tagtime'] = gt.dtime.strftime('%d%m%Y')
		for key in result.keys():
			result[key] = OrderedDict(sorted(result[key].iteritems(), key=lambda x: x))
		return result, worldwide



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
	def search_trends(search_value):
		trends = Trend.objects.filter(name__contains=search_value)
		return [{'name':e.name, 'id': e.id} for e in trends][:TREND_SEARCH_LIMIT]


	@staticmethod
	def where_trend(trendid, trendname):
		places = Trend.obj


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
		return week_trends, place.another_name


	@staticmethod
	def get_tendency(trendid):
		flag = True
		result = {'time':[], 'volume':[]}
		trends = GeoTrend.objects.filter(trend_id=trendid).order_by('volume')
		for trend in trends:
			if not trend.volume:
				flag = False
				break
			timejs = int(time.mktime(trend.dtime.timetuple())) * 1000.0
			result['time'].append(timejs)
			result['volume'].append(trend.volume)
		return result, flag
		#return {'time':[1,2,3,4,5,6,7,8,9,10], 'volume':[1,2,3,4,5,6,5,4,3,2]}, True



class Clusters(models.Model):
	name = models.CharField(unique=True, max_length=255)
	valid = models.IntegerField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'clusters'

	def __unicode__(self):
		return u'{0}'.format(self.name)

	@staticmethod
	def get_wordtrend_clusters(trendid):
		clusters = {}
		trendwords = TrendWord.objects.filter(trend_id=trendid)
		for tw in trendwords:
			word = Word.objects.filter(id=tw.word_id).first()
			tWords = TrendWord.objects.filter(word_id=word.id)
			trends = []
			for two in tWords:
				t = Trend.objects.filter(id=two.trend_id).first()
				trends.append({'name':t.name, 'id':t.id})
			cluster = Clusters.objects.filter(id=word.clusters_id).first()
			if not clusters.get(cluster.name): clusters[cluster.name] = []
			clusters[cluster.name].append({'word':word.name, 'trends':trends[:]})
		return clusters

	@staticmethod
	def get_trend_clusters(trendid):
		clusters = {}
		trendwords = TrendWord.objects.filter(trend_id=trendid)
		for tw in trendwords:
			word = Word.objects.filter(id=tw.word_id).first()
			cluster = Clusters.objects.filter(id=word.clusters_id).first()
			tWords = TrendWord.objects.filter(word_id=word.id)
			trends = []
			if not clusters.get(cluster.name): clusters[cluster.name] = []
			for two in tWords:
				if two.trend_id == int(trendid): continue
				t = Trend.objects.filter(id=two.trend_id).first()
				newt = {'name':t.name, 'id':t.id}
				if newt not in clusters[cluster.name]:
					trends.append(newt)
			clusters[cluster.name] += trends
			for cluster in clusters.keys():
				if not clusters[cluster]: del clusters[cluster]
		return clusters



class TrendWord(models.Model):
	trend = models.ForeignKey(Trend, models.DO_NOTHING)
	word = models.ForeignKey('Word', models.DO_NOTHING)

	class Meta:
		managed = False
		db_table = 'trendword'
		unique_together = (('word', 'trend'),)


class Word(models.Model):
	name = models.CharField(unique=True, max_length=255)
	clusters = models.ForeignKey(Clusters, models.DO_NOTHING)

	class Meta:
		managed = False
		db_table = 'word'

	def __unicode__(self):
		return u'{0}'.format(self.name)

