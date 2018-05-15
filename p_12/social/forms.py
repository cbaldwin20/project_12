from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from . import models

class UserCreateForm(UserCreationForm):
	"""I am overriding the standard UserCreationForm
	to manipulate the fields a bit"""
	class Meta:
		fields = ("username", "email", "password1", "password2")
		model = User 

	def __init__(self, *args, **kwargs):
		#here we are changing the labels on these two fields
		super().__init__(*args, **kwargs)
		self.fields['username'].label = "Display name"
		self.fields['email'].label = "Email address"

class ProfileForm(forms.ModelForm):
	class Meta:
		fields = ("name", "description")
		model = models.Profile

class SkillForm(forms.ModelForm):
	class Meta:
		fields = ("name",)
		model = models.Skill 


class ProjectForm(forms.ModelForm):
	class Meta:
		fields = (
			"project_name", "description", "project_timeline", "application_requirements",
			"skills", "url", "active")
		model = models.Project

		
class ProfileMyProjectsForm(forms.ModelForm):
	class Meta:
		fields = (
			"project_name",
			"url")
		model = models.Project

	def clean(self, *args, **kwargs):
		data = self.cleaned_data
		project_name = data.get('project_name', None)
		url = data.get('url', None)
		if project_name and url:
			try:
				models.Project.objects.get(project_name=project_name, url=url)
			except models.Project.DoesNotExist:
				raise forms.ValidationError('This project with url: {}, project name: {}, does not exist.'.format(url, project_name))
		return super().clean(*args, **kwargs)

