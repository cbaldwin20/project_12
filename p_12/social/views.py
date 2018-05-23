
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify

from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory

from datetime import timedelta
from django.utils import timezone

import datetime
import time

import operator
import functools

from . import models
from . import forms 


@login_required
def practice(request):
    Skills_form = modelformset_factory(
        models.Skill,
        form=forms.SkillForm,
        extra=1,
        )
    
    skills_formset1 = Skills_form(queryset=models.Skill.objects.none(), prefix='skills_formset1')

    return render(request, 'practice.html', {'skills_formset1': skills_formset1})


@login_required
def index(request, need="All Needs"):
    try:
        models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        return redirect('base:profile_new')
    needs_list = ["All Needs", "Android Developer", "Designer", "Java Developer", 
    "PHP Developer", "Python Developer", "Rails Developer", "WordPress Developer", 
    "iOS Developer"]
    if need != "All Needs":
        positions = models.Position.objects.filter(position_name__icontains=need,
            position_description__icontains=need, position_filled_user__isnull=True)
        return render(request, 'index.html', {'positions':positions, 'need':need, 'needs_list':needs_list})
    
    my_skills = models.Skill.objects.filter(user_skills__user=request.user)
    if my_skills:
        my_skills_name_list = []
        for skill in my_skills:
            my_skills_name_list += skill.name
        query = functools.reduce(operator.and_, (
            Q(position_name__icontains=the_skill)|Q(position_description__icontains=the_skill) for the_skill in my_skills_name_list))
        positions = models.Position.objects.filter(query, position_filled_user__isnull=True)
        return render(request, 'index.html', {'positions':positions, 'need':need, 'needs_list':needs_list})

    positions = None
    return render(request, 'index.html', {'positions': positions})

@login_required
def project_new(request):
    project_form = forms.ProjectForm(prefix='project_form')
    Positions_form = modelformset_factory(
        models.Position,
        form=forms.PositionForm,
        )
    positions_formset = Positions_form(prefix='positions_formset')

    if request.method == "POST":
        positions_formset = Positions_form(request.POST, prefix='positions_formset')
        project_form = forms.ProjectForm(request.POST, prefix='project_form')
        if positions_formset.is_valid():
            if project_form.is_valid():
                user_project = project_form.save(commit=False)
                user_project.creator = request.user
                user_project.active = True
                now = datetime.datetime.now()
                seconds = int(time.mktime(now.timetuple())) 
                user_project.url_slug = "{}-{}".format(seconds, slugify(user_project.project_name))
                user_project.save()

                for position in positions_formset:
                    if position.cleaned_data:
                        the_position = position.save(commit=False)
                        the_position.project = user_project
                        the_position.save()

                        if the_position.position_name == "":
                            if the_position.position_description == "":
                                the_position.delete()

                for position in positions_formset.deleted_forms:
                    if position.is_valid():
                        delete_position = position.save()
                        delete_position.delete()
                return redirect('base:project', url_slug=user_project.url_slug )
    return render(request, 'project_new.html', {'project_form': project_form, 'positions_formset': positions_formset })

@login_required
def project_edit(request, url_slug):
    try:
        this_project = models.Project.objects.get(creator=request.user, url_slug=url_slug)
    except models.Project.DoesNotExist:
        return redirect('base:project_new')

    project_form = forms.ProjectForm(instance=this_project, prefix='project_form')
    Positions_form = modelformset_factory(
        models.Position,
        form=forms.PositionForm,
        )
    positions = models.Position.objects.filter(project=this_project)
    positions_formset = Positions_form(queryset=positions, prefix='positions_formset')

    if request.method == "POST":
        positions_formset = Positions_form(request.POST, queryset=positions, prefix='positions_formset')
        project_form = forms.ProjectForm(request.POST, instance=this_project, prefix='project_form')
        if positions_formset.is_valid():
            if project_form.is_valid():
                user_project = project_form.save()

                for position in positions_formset:
                    if position.cleaned_data:
                        the_position = position.save(commit=False)
                        the_position.project = user_project
                        the_position.save()

                        if the_position.position_name == "":
                            if the_position.position_description == "":
                                the_position.delete()

                for position in positions_formset.deleted_forms:
                    if position.is_valid():
                        delete_position = position.save()
                        delete_position.delete()
                return redirect('base:project', url_slug=user_project.url_slug )
    print("*************************Got to right before the render.")
    return render(request, 'project_edit.html', {'project_form': project_form, 'positions_formset': positions_formset })
    

def project(request, url_slug):
    the_project = get_object_or_404(models.Project, url_slug=url_slug)
    return render(request, 'project.html', {'the_project': the_project})

@login_required
def project_delete(request, url_slug):
    try:
        project_delete = models.Project.objects.get(creator=request.user, url_slug=url_slug)
    except models.Project.DoesNotExist:
        return redirect('base:home')

    for position in project_delete.project_positions:
        for application in position.position_applications:
            application.delete()
        position.delete()
    project_delete.delete()

    return redirect("base:home")





@login_required
def profile_new(request):

    try:
        models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        # making this an empty list for the sake of the template. I share the 
        # template with def profile_edit
        previous_jobs = []
    else:
        print("SO RIGHT HERE IT IS THROWING THIS ERROR**********")
        return redirect('base:profile_edit')

    

    Projects_form = modelformset_factory(
        models.Project,
        form=forms.ProfileMyProjectsForm,
        extra=1,
        )
    
    Skills_form = modelformset_factory(
        models.Skill,
        form=forms.SkillForm,
        extra=1,
        )

    user_profile_form = forms.ProfileForm(prefix='user_profile_new')
    projects_formset = Projects_form(queryset=models.Project.objects.none(), prefix='projects_formset_new')
    skills_formset = Skills_form(queryset=models.Skill.objects.none(), prefix='skills_formset_new')

    if request.method == "POST":
        user_profile_form = forms.ProfileForm(request.POST, request.FILES, prefix='user_profile_new')
        projects_formset = Projects_form(request.POST, prefix='projects_formset_new')
        skills_formset = Skills_form(request.POST,  prefix='skills_formset_new')

        if user_profile_form.is_valid():
            print("*****************Got to right before the projects_formset")
            if projects_formset.is_valid():
                print("*****************Got to right after the projects_formset")
                if skills_formset.is_valid():
                    final_user_profile = user_profile_form.save(commit=False)
                    final_user_profile.user = request.user
                    now = datetime.datetime.now()
                    seconds = int(time.mktime(now.timetuple())) 
                    final_user_profile.url_slug = "{}-{}".format(seconds, slugify(final_user_profile.name))
                    # here we have our profile for our user, ready for the projects
                    # and skills manytomany fields to be added. 
                    final_user_profile.save()

                    for project in projects_formset:
                        if project.is_valid():
                            if project.cleaned_data:
                                # I'm not creating a new project here, just 
                                # adding the the profile's projects manytomanyfield
                                project = project.save(commit=False)
                                final_user_profile.projects.add(project)

                    for skill in skills_formset:
                        if skill.is_valid():
                            if skill.cleaned_data:
                                #****I may need to add 'user', etc.
                                name = skill.cleaned_data['name'].lower()
                                if name == "":
                                    # if the user erases one of the skills fields
                                    # then don't delete the skill but delete the 
                                    # instance in the profile's manytomanyfield. 
                                    pass
                                else:
                                    print("*****************skill name {}.".format(name))
                                    try:
                                        # see if this skill already exists, so we don't have
                                        # to create a new one. 
                                        skill_replace = models.Skill.objects.get(name=name)
                                        print("*****************skill did exist.")
                                    except models.Skill.DoesNotExist:
                                        # if skill does not exist, then create it in the Skill model. 
                                        skill_replace = models.Skill.objects.create(name=name)
                                        print("*****************skill did not exist.")
                                    
                                    # I'll have to find a better way to do this, but I'm 
                                    # just deleting the many to many instance and replacing it with
                                    # the new one, even if its the same instance. This is in case
                                    # they delete or erase an instance. 
                                    
                                    final_user_profile.skills.add(skill_replace)
                                    print("*****************saved the skill.")
                                    
                    return redirect('base:profile', url_slug=final_user_profile.url_slug)

    return render(request, 'profile_edit.html', {'user_profile_form': user_profile_form, 'projects_formset': projects_formset, 'skills_formset': skills_formset, 'previous_jobs': previous_jobs })

@login_required
def profile_edit(request):
    # see if this user already has a profile. 
    try:
        user_profile = models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        return redirect('base:profile_new')

    # 'previous_jobs' not used yet. 
    previous_jobs = models.Position.objects.filter(
        position_filled_user=request.user
        )
    
    
    Projects_form = modelformset_factory(
        models.Project,
        form=forms.ProfileMyProjectsForm,
        extra=1,
        can_delete=True,
        
        )
    
    Skills_form = modelformset_factory(
        models.Skill,
        form=forms.SkillForm,
        extra=1,
        can_delete=True,
        )
    # this is the main profile. Is not a formset. 
    
   
    # if the user has a profile then get all the projects and skills of the user
    # and put them into formsets. 
    
    user_profile_form = forms.ProfileForm(instance=user_profile,prefix='user_profile')
    projects_formset = Projects_form(queryset=user_profile.projects.all(), prefix='projects_formset')
    skills_formset = Skills_form(queryset=user_profile.skills.all(), prefix='skills_formset')
        
    

    if request.method == "POST":
        user_profile_form = forms.ProfileForm(request.POST, request.FILES, instance=user_profile, prefix='user_profile')
        projects_formset = Projects_form(request.POST, queryset=user_profile.projects.all(), prefix='projects_formset')
        skills_formset = Skills_form(request.POST, queryset=user_profile.skills.all(), prefix='skills_formset')
        if user_profile_form.is_valid():
            print("*****************Got to right before the projects_formset")
            if projects_formset.is_valid():
                print("*****************Got to right after the projects_formset")
                if skills_formset.is_valid():
                    final_user_profile = user_profile_form.save()

                    for project in projects_formset:
                        if project.is_valid():
                            if project.cleaned_data:
                                # I'm not creating a new project here, just 
                                # adding the the profile's projects manytomanyfield
                                project = project.save(commit=False)
                                final_user_profile.projects.add(project)

                    for skill in skills_formset:
                        if skill.is_valid():
                            if skill.cleaned_data:
                                #****I may need to add 'user', etc.
                                name = skill.cleaned_data['name'].lower()
                                if name == "":
                                    # if the user erases one of the skills fields
                                    # then don't delete the skill but delete the 
                                    # instance in the profile's manytomanyfield. 
                                    skill = skill.save(commit=False)
                                    final_user_profile.skills.remove(skill)
                                    print("*****************deleted the skill from the user profile.")
                                else:
                                    print("*****************skill name {}.".format(name))
                                    try:
                                        # see if this skill already exists, so we don't have
                                        # to create a new one. 
                                        skill_replace = models.Skill.objects.get(name=name)
                                        print("*****************skill did exist.")
                                    except models.Skill.DoesNotExist:
                                        # if skill does not exist, then create it in the Skill model. 
                                        skill_replace = models.Skill.objects.create(name=name)
                                        print("*****************skill did not exist.")
                                    skill = skill.save(commit=False)
                                    # I'll have to find a better way to do this, but I'm 
                                    # just deleting the many to many instance and replacing it with
                                    # the new one, even if its the same instance. This is in case
                                    # they delete or erase an instance. 
                                    final_user_profile.skills.remove(skill)
                                    final_user_profile.skills.add(skill_replace)
                                    print("*****************saved the skill.")
                                    
                    for skill in skills_formset.deleted_forms:
                        print("*****************got past the .deleted_forms.")
                        if skill.is_valid():
                            skill_remove = skill.save()
                            final_user_profile.skills.remove(skill_remove)
                            print("*****************removed the skill.")

                    return redirect('base:profile', url_slug=final_user_profile.url_slug)

    return render(
        request, 'profile_edit.html', 
        {'user_profile_form': user_profile_form, 'projects_formset': projects_formset, 'skills_formset': skills_formset, 'previous_jobs': previous_jobs })
                    


#******I need to make a form validator that if the profile project does not already
#****** exist with the url given then throw an error. 





    


def profile(request, url_slug=None):
    # if there is no url_slug provided then just go to 
    # either my profile, and if I don't have a profile then go to 
    # create my profile. 
    profile = get_object_or_404(models.Profile, url_slug=url_slug)
    my_projects = models.Project.objects.filter(creator=request.user)
    positions = models.Position.objects.filter(position_filled_user=request.user)
    return render(request, 'profile.html', {'profile': profile, 'positions': positions, 'my_projects': my_projects })




def search(request, need="All Needs"):
    """activates when search field is used """
    need=need 
    term = request.GET.get('q')
    matches = models.Project.objects.filter(
        Q(project_name__icontains=term)|Q(description__icontains=term)|
        Q(application_requirements__icontains=term)|
        Q(project_positions__position_name__icontains=term)|
        Q(project_positions__position_description__icontains=term))

    if need != "All Needs":
        matches = matches.filter(
        Q(project_positions__position_name__icontains=need)|
        Q(project_positions__position_description__icontains=need))

    all_needs = ["All Needs", "Android Developer", "Designer", "Java Developer", 
    "PHP Developer", "Python Developer", "Rails Developer", "WordPress Developer", "iOS Developer"]

    return render(request, 'search.html', {'matches': matches, 'term': term,
     'all_needs': all_needs,
     'need': need })




@login_required
def applications(request, applications="New Applications", project="All Projects", need="All Needs"):
    applications=applications
    project=project
    need=need
    # for the slug_url anchor to my profile. 
    profile = models.Profile.objects.get(user=request.user)


    all_applications = models.Application.objects.filter(
        position__project__creator=request.user)

    #************ filter the applications
    if applications == "New Applications":
        all_applications = all_applications.filter(
            applied_date__gte=timezone.now().date() - timedelta(days=7))
    elif applications == "Accepted":
        all_applications = all_applications.filter(accepted=True)
    elif applications == "Rejected":
        all_applications = all_applications.filter(accepted=False)

    #************ filter project
    if project != "All Projects":
        all_applications = all_applications.filter(position__project__project_name=project)

    #************* filter need
    if need != "All Needs":
        all_applications = all_applications.filter(position__position_name__icontains=need,
            position__position_description__icontains=need)

    all_projects = models.Project.objects.filter(creator=request.user)

    all_needs = ["All Needs", "Android Developer", "Designer", 
    "Java Developer", "PHP Developer", "Python Developer", "Rails Developer", 
    "WordPress Developer", "iOS Developer"]

    statuses = ["All Applications", "New Applications", "Accepted", "Rejected"]

    return render(request, 'applications.html', 
        {'applications': applications, "project": project, "need": need, 
        "all_projects": all_projects, 'all_applications': all_applications,
        "all_needs": all_needs, "statuses": statuses, 'profile': profile })

# class LoginView(generic.FormView):
#     form_class = AuthenticationForm 
#     success_url = reverse_lazy("base:index")
#     template_name = "accounts/login.html"

#     def get_form(self, form_class=None):
#         if form_class is None:
#             form_class = self.get_form_class()
#         return form_class(self.request, **self.get_form_kwargs())

#     def form_valid(self, form):
#         login(self.request, form.get_user())
#         return super().form_valid(form)


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

