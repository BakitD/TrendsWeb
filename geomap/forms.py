from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
	name = forms.CharField(label='Name', max_length=64, \
				widget=forms.TextInput(attrs={'required':True}))
	email = forms.EmailField(label='Email', max_length=64, \
				widget=forms.EmailInput(attrs={'required':True}))
	username = forms.CharField(label='Login', max_length=64, \
				widget=forms.TextInput(attrs={'required':True}))
	password1 = forms.CharField(label='Password', \
				widget=forms.PasswordInput(attrs={'required':True}), )
	password2 = forms.CharField(label='Password confirmation', \
				widget=forms.PasswordInput(attrs={'required':True}))

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).first():
			raise forms.ValidationError('Email %s is already in use' % email)
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username).first():
			raise forms.ValidationError('Login %s is already in use' % username)
		return username

	def clean(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password1 != password2:
			raise forms.ValidationError('Passwords do not match')
		return self.cleaned_data



class PasswordResetForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(PasswordResetForm, self).__init__(*args, **kwargs)

	password1 = forms.CharField(label='Password', \
				widget=forms.PasswordInput(attrs={'required':True}), )
	password2 = forms.CharField(label='Password confirmation', \
				widget=forms.PasswordInput(attrs={'required':True}))

	def clean(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password1 != password2:
			raise forms.ValidationError('Passwords do not match')
		return self.cleaned_data

	def save(self, commit=True):
		self.user.set_password(self.cleaned_data['password1'])
		if commit:
			self.user.save()
		return self.user



class ProfileEditForm(RegisterForm):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ProfileEditForm, self).__init__(*args, **kwargs)

	password1 = forms.CharField(label='New password', required=False,\
					widget=forms.PasswordInput)
	password2 = forms.CharField(label='New password confirmation', required=False,\
					widget=forms.PasswordInput)
	current_password = forms.CharField(label='Current password', \
				widget=forms.PasswordInput(attrs={'required':True}))

	def clean_email(self):
		email = self.cleaned_data.get('email')
		user = User.objects.filter(email=email).first()
		if user and user != self.user:
			raise forms.ValidationError('Email %s is already in use' % email)
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		user = User.objects.filter(username=username).first()
		if user and user != self.user:
			raise forms.ValidationError('Login %s is already in use' % username)
		return username

	def clean_current_password(self):
		current_password = self.cleaned_data.get('current_password')
		if not self.user.check_password(current_password):
			raise forms.ValidationError('Incorrect current password')
		return current_password


	def clean(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and not password2 or not password1 and password2:
			raise forms.ValidationError('All password fields are required to be filled')
		if password1 and password1 != password2:
			raise forms.ValidationError('New passwords do not match')
		return self.cleaned_data




