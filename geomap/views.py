from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from .forms import RegisterForm, ProfileEditForm, PasswordResetForm
from django.forms.forms import NON_FIELD_ERRORS

import json
from django_redis import get_redis_connection
redis = get_redis_connection('default')

from models import TrendModel

def init_trends():
	data = json.loads(redis.get('geomap'))
	for woeid, d in data.iteritems():
		if d['trends']:
			print woeid, ', lnlt:, ',(d['coordinates']), ' trends: ', d['trends']

#TODO make this
#init_trends()


# SELF-DEFINED FUNCTIONS
def anonymous_required(user):
	return user.is_anonymous()

# VIEWS
def index(request):
	trends = TrendModel.objects.all()
	return render(request, 'geomap/home.html', {'trends' : trends})

@login_required
def logoutview(request):
	logout(request)
	return redirect('index')


@user_passes_test(anonymous_required)
def loginview(request):
	login_errors = []
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if not user:
			login_errors.append('Invalid credentials')
		elif user.is_active:
			login(request, user)
	return render(request, 'geomap/home.html', {'login_errors' : login_errors})



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




