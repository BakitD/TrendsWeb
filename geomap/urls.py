from django.conf.urls import url

from .import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.loginview, name='loginview'),
	url(r'^logout/$', views.logoutview, name='logoutview'),
	url(r'^profile/$', views.profile, name='profile'),
	url(r'^profile/delete/$', views.profile_delete, name='profile_delete'),
	url(r'^places/$', views.places, name='places'),
	url(r'^places/(?P<woeid>\d+)/$', views.citytrends, name='citytrends'),


	url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            views.reset_confirm, name='reset_confirm'),
        url(r'^reset/$', views.reset, name='reset'),
]