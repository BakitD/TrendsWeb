from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.conf import settings
from .forms import RegisterForm, ProfileEditForm, PasswordResetForm
from models import Place, Trend
from trendstore import tStore
import json

mapConfig = settings.MAP_CONFIG
mapConfig['scales'] = tStore.get_scales()



# SELF-DEFINED FUNCTIONS
def anonymous_required(user):
	return user.is_anonymous()


# VIEWS TODO
def index(request):
	login_errors = request.session.pop('login_errors', None)
	trends = tStore.get_trends_by_layer(0)
	return render(request, 'geomap/home.html', 
			{'trends' : json.dumps(trends), 
			'login_errors':login_errors,
			'mapConfig' : mapConfig,
			'authUserFlag' : int(request.user.is_authenticated())
			})


@login_required
def logoutview(request):
	logout(request)
	return redirect('index')


@user_passes_test(anonymous_required)
def loginview(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if not user:
			request.session['login_errors'] = ['Invalid credentials',]
		elif user.is_active:
			login(request, user)
	return redirect('index')



@user_passes_test(anonymous_required)
def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			name = form.cleaned_data.get('name')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password1')
			user = User.objects.create_user(username, email, password, first_name=name)
			user.save()
			return redirect('index')
	else:
		form = RegisterForm()
	return render(request, 'geomap/register.html', {'reg_form' : form})


@login_required
def profile(request):
	form = updateflag = False
	if request.method == 'POST':
		form = ProfileEditForm(request.POST, user=request.user)
		if form.is_valid():
			user = request.user
			user.username = form.cleaned_data.get('username')
			user.first_name = form.cleaned_data.get('name')
			user.email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password1')
			if password:
				user.set_password(password)
				update_session_auth_hash(request, user)
			user.save()
			updateflag = True
	user = request.user
	if not form:	
		form = ProfileEditForm(initial={'email' : user.email, \
					'username':user.username, 'name' : user.first_name})
	return render(request, 'geomap/profile.html', {'profile_form' : form, 'updateflag' : updateflag})


@login_required
def profile_delete(request):
	user = request.user
	try:
		logout(request)
		user.delete()
	except:
		pass
	return redirect('index')


@login_required
def places(request):
	return render(request, 'geomap/places.html', {'countries' : Place.get_countries()})


@login_required
def citytrends(request, country, woeid):
	places = Place.get_citytrends(woeid)
	country_data = Place.get_countrytrends(woeid)
	if country_data.get('trends'): places.insert(0, country_data)
	return render(request, 'geomap/citytrends.html', {'placetrends' : places, 'country' : country})


@login_required
def placehistory(request, place, woeid):
	week_trends = Trend.get_weektrends(woeid)
	return render(request, 'geomap/placehistory.html', {'place' : place, 'week_trends' : week_trends})


@user_passes_test(anonymous_required)
def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, 
	template_name='geomap/password_reset_confirm.html',
	set_password_form=PasswordResetForm,
        uidb64=uidb64, token=token, post_reset_redirect=reverse('index'))


@user_passes_test(anonymous_required)
def reset(request):
    return password_reset(request, template_name='geomap/password_reset_form.html',
        email_template_name='geomap/password_reset_email.html',
        subject_template_name='geomap/subject_reset.txt',
        post_reset_redirect=reverse('index'))



# View for AJAX on map zooming
@login_required
def ajax_map_zoom(request):
	swLat = float(request.POST.get('southWestLatitude'))
	swLng = float(request.POST.get('southWestLongitude'))
	neLat =  float(request.POST.get('northEastLatitude'))
	neLng = float(request.POST.get('northEastLongitude'))
	scale = int(request.POST.get('scale'))
	trends = tStore.get_places(scale, swLat, swLng, neLat, neLng)
	return HttpResponse(json.dumps({'trends' : trends}))



