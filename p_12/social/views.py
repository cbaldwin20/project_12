from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from . import forms 

def signup(request):
	return render(request, 'signup.html')

def signin(request):
	return render(request, 'signin.html')

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
	return render(request, 'profile_edit.html')

def profile(request):
	return render(request, 'profile.html')

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
	url = reverse_lazy('home')

	def get(self, request, *args, **kwargs):
		logout(request)
		return super().get(request, *args, **kwargs)


class SignUp(generic.CreateView):
	form_class = forms.UserCreateForm
	success_url = reverse_lazy('base:login')
	template_name = 'signup.html'

