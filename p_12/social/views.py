from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory

from . import models
from . import forms 


@login_required
def index(request):
	return render(request, 'index.html')

def search(request):
	return render(request, 'search.html')

def project_new(request):
	return render(request, 'project_new.html')

def project_edit(request):
	return render(request, 'project_edit.html')

def project(request):
	return render(request, 'project.html')

def profile_edit(request):
	previous_jobs = models.Application.objects.filter(
		person_applying=request.user,
		accepted=True, 
		project__active=False)
	try:
		user_profile = models.Profile.objects.get(user=request.user)
	except models.Profile.DoesNotExist:
		user_profile = None
	
	Projects_form = modelformset_factory(
		models.Project,
		form=forms.ProfileMyProjectsForm,
		
		)
	
	Skills_form = modelformset_factory(
		models.Skill,
		form=forms.SkillForm,
		)
	user_profile = models.Profile.objects.first()
	user_profile_form = forms.ProfileForm(instance=user_profile,prefix='user_profile')
	if user_profile:
		projects_formset = Projects_form(queryset=user_profile.projects.all(), prefix='projects_formset')
		skills_formset = Skills_form(queryset=user_profile.skills.all(), prefix='skills_formset')
	else:
		projects_formset = Projects_form(prefix='projects_formset')
		skills_formset = Skills_form(prefix='skills_formset')

	if request.method == "POST":
		if user_profile:
			user_profile_form = forms.ProfileForm(request.POST, request.FILES, instance=user_profile, prefix='user_profile')
			projects_formset = Projects_form(request.POST, queryset=user_profile.projects.all(), prefix='projects_formset')
			skills_formset = Skills_form(request.POST, queryset=user_profile.skills.all(), prefix='skills_formset')
		else:
			print("*****************It used the else.")
			user_profile_form = forms.ProfileForm(request.POST, request.FILES, prefix='user_profile')
			projects_formset = Projects_form(request.POST, prefix='projects_formset')
			skills_formset = Skills_form(request.POST,  prefix='skills_formset')
		if user_profile_form.is_valid():
			print("*****************Got to right before the projects_formset")
			if projects_formset.is_valid():
				print("*****************Got to right after the projects_formset")
				if skills_formset.is_valid():
					final_user_profile = user_profile_form.save(commit=False)
					final_user_profile.user = request.user 
					final_user_profile.save()

					for project in projects_formset:
						if project.is_valid():
							if project.cleaned_data:
								#****I may need to add 'user', etc. 
								project = project.save()
								final_user_profile.projects.add(project)

					for skill in skills_formset:
						if skill.is_valid():
							if skill.cleaned_data:
								#****I may need to add 'user', etc.
								name = skill.cleaned_data['name'].lower()
								if name == "":
									skill = skill.save(commit=False)
									final_user_profile.skills.remove(skill)
									print("*****************deleted the skill from the user profile.")
								else:
									print("*****************skill name {}.".format(name))
									try:
										skill_replace = models.Skill.objects.get(name=name)
										print("*****************skill did exist.")
									except models.Skill.DoesNotExist:
										skill_replace = models.Skill.objects.create(name=name)
										print("*****************skill did not exist.")
									skill = skill.save(commit=False)
									final_user_profile.skills.remove(skill)
									final_user_profile.skills.add(skill_replace)
									print("*****************saved the skill.")
									
									

					return redirect('base:home')

	return render(
		request, 'profile_edit.html', 
		{'user_profile': user_profile, 'user_profile_form': user_profile_form, 'projects_formset': projects_formset, 'skills_formset': skills_formset, 'previous_jobs': previous_jobs })
					


#******I need to make a form validator that if the profile project does not already
#****** exist with the url given then throw an error. 





	























def profile(request):
	pass

def profile_new(request):
	pass






def applications(request):
	return render(request, 'applications.html')

# class LoginView(generic.FormView):
# 	form_class = AuthenticationForm 
# 	success_url = reverse_lazy("base:index")
# 	template_name = "accounts/login.html"

# 	def get_form(self, form_class=None):
# 		if form_class is None:
# 			form_class = self.get_form_class()
# 		return form_class(self.request, **self.get_form_kwargs())

# 	def form_valid(self, form):
# 		login(self.request, form.get_user())
# 		return super().form_valid(form)


class LogoutView(generic.RedirectView):
	"""Made this logout class so I can redirect to the 
	home page. The automatic auth method redirects 
	inappropriately """
	url = reverse_lazy('login')

	def get(self, request, *args, **kwargs):
		logout(request)
		return super().get(request, *args, **kwargs)


class SignUp(generic.CreateView):
	form_class = forms.UserCreateForm
	success_url = reverse_lazy('login')
	template_name = 'registration/signup.html'

