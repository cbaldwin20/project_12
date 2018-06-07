
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify

from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory

from django.db.models import Q

from datetime import timedelta
from django.utils import timezone

import datetime
import time

from django.contrib import messages

import operator
import functools

from . import models
from . import forms 





@login_required
def index(request, need="All Needs"):
    try:
        my_profile = models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        return redirect('base:profile_new')
    
    
    needs_list = ["All Needs"]
    my_skills = my_profile.skills.all()
    for skill in my_skills:
        needs_list.append(skill.name)
    
    
    if need != "All Needs":
        positions = models.Position.objects.filter(
            Q(position_name__icontains=need)|
            Q(position_description__icontains=need),
             position_filled_user__isnull=True).exclude(project__creator=request.user)
        return render(request, 'index.html', {'positions':positions, 'need':need, 'needs_list':needs_list})


    elif my_skills:
        my_skills_name_list = []
        for skill in my_skills:
            my_skills_name_list.append(skill.name)
        query = functools.reduce(operator.or_, (
            Q(position_name__icontains=the_skill)|Q(position_description__icontains=the_skill) for the_skill in my_skills_name_list))
        positions = models.Position.objects.filter(query, position_filled_user__isnull=True).exclude(project__creator=request.user)
        return render(request, 'index.html', {'positions':positions, 'need':need, 'needs_list':needs_list})

    else:
        positions = None
    return render(request, 'index.html', {'positions': positions})

@login_required
def project_new(request):
    project_form = forms.ProjectForm(prefix='project_form')
    Positions_form = modelformset_factory(
        models.Position,
        form=forms.PositionForm,
        )
    positions_formset = Positions_form(queryset=models.Position.objects.none(), prefix='positions_formset')

    if request.method == "POST":
        positions_formset = Positions_form(request.POST, prefix='positions_formset')
        project_form = forms.ProjectForm(request.POST, prefix='project_form')
        if positions_formset.is_valid():
            if project_form.is_valid():
                user_project = project_form.save(commit=False)
                user_project.creator = request.user
                now = datetime.datetime.now()
                seconds = int(time.mktime(now.timetuple())) 
                user_project.url_slug = "{}-{}".format(seconds, slugify(user_project.project_name))
                user_project.save()
                profile_to_link = models.Profile.objects.get(user=request.user)
                user_project.user_projects.add(profile_to_link)

                for position in positions_formset:
                    if position.cleaned_data:
                        the_position = position.save(commit=False)
                        the_position.position_name = the_position.position_name.lower()
                        the_position.project = user_project
                        the_position.save()

                        if the_position.position_name == "":
                            if the_position.position_description == "":
                                the_position.delete()

                for position in positions_formset.deleted_forms:
                    if position.is_valid():
                        delete_position = position.save()
                        delete_position.delete()
                messages.success(request, 'Project created!')
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
                profile_to_link = models.Profile.objects.get(user=request.user)
                user_project.user_projects.add(profile_to_link)

                for position in positions_formset:
                    if position.cleaned_data:
                        the_position = position.save(commit=False)
                        the_position.position_name = the_position.position_name.lower()
                        the_position.project = user_project
                        the_position.save()

                        if the_position.position_name == "":
                            if the_position.position_description == "":
                                applications = models.Application.objects.filter(
                                    position=the_position)
                                if applications:
                                    for application in applications:
                                        application.delete()
                                the_position.delete()

                for position in positions_formset.deleted_forms:
                    if position.is_valid():
                        delete_position = position.save()
                        applications = models.Application.objects.filter(
                                    position=delete_position)
                        if applications:
                            for application in applications:
                                application.delete()
                        delete_position.delete()
                messages.success(request, 'Project updated!')
                return redirect('base:project', url_slug=user_project.url_slug )
    print("*************************Got to right before the render.")
    return render(request, 'project_edit.html', {'project_form': project_form, 'positions_formset': positions_formset })
    

def project(request, url_slug, position_pk=None, action=None):
    if position_pk:
        the_position = models.Position.objects.get(id=position_pk)
        if action == "apply":
            models.Application.objects.create(
                position=the_position,
                person_applying=request.user,
                )
            messages.success(request, 'You applied for {}'.format(the_position.position_name))
        elif action == "unapply":
            app_to_delete = models.Application.objects.get(position=the_position)
            app_to_delete.delete()
            messages.success(request, 'You unapplied for {}'.format(the_position.position_name))

        elif action == "undo":
            app_to_change = models.Application.objects.get(position=the_position)
            app_to_change.accepted = False
            app_to_change.rejected = False
            app_to_change.save()

            the_position.position_filled_user = None
            the_position.save()

            models.Notification.objects.create(
                    person_notifying = app_to_change.person_applying,
                    description = "Your application '{}' for project '{}' has been changed to undecided.".format(
                        app_to_change.position.position_name, app_to_change.position.project.project_name),
                    )

            messages.success(request, "You made {}'s application for {} into 'undecided'".format(app_to_change.person_applying.profile_user.name, the_position.position_name))

    the_project = get_object_or_404(models.Project, url_slug=url_slug)
    return render(request, 'project.html', {'the_project': the_project})

@login_required
def project_delete(request, url_slug):
    try:
        project_delete = models.Project.objects.get(creator=request.user, url_slug=url_slug)
    except models.Project.DoesNotExist:
        return redirect('base:home')

    for position in project_delete.project_positions.all():
        for application in position.position_applications:
            application.delete()
        position.delete()
    messages.success(request, 'You deleted project: {}'.format(project_delete.project_name))
    project_delete.delete()

    return redirect("base:home")


@login_required
def my_profile(request):
    try:
        my_profile = models.Profile.objects.get(user=request.user)
    except models.Profile.DoesNotExist:
        return redirect('base:profile_new')

    return redirect('base:profile', url_slug=my_profile.url_slug)



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
        models.OutsideProject,
        form=forms.ProfileMyProjectsForm,
        extra=1,
        )
    
    Skills_form = modelformset_factory(
        models.Skill,
        form=forms.SkillForm,
        extra=1,
        )

    user_profile_form = forms.ProfileForm(prefix='user_profile_new')
    projects_formset = Projects_form(queryset=models.OutsideProject.objects.none(), prefix='projects_formset_new')
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
                                project.creator = request.user
                                project.save()

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
                                    
                    messages.success(request, 'You created your profile!')
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
        models.OutsideProject,
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
    projects_formset = Projects_form(queryset=user_profile.user.outsideproject_owner.all(), prefix='projects_formset')
    skills_formset = Skills_form(queryset=user_profile.skills.all(), prefix='skills_formset')
        
    

    if request.method == "POST":
        user_profile_form = forms.ProfileForm(request.POST, request.FILES, instance=user_profile, prefix='user_profile')
        projects_formset = Projects_form(request.POST, queryset=user_profile.user.outsideproject_owner.all(), prefix='projects_formset')
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
                                project_name = project.cleaned_data['project_name']
                                if project_name.strip() == "":
                                    project_delete = project.save(commit=False)
                                    project_delete.delete()

                                elif project_name != "":
                                    final_project = project.save(commit=False)
                                    final_project.creator = request.user
                                    final_project.save()
                                
                    for project in projects_formset.deleted_forms:
                        if project.is_valid():
                            project_to_delete = project.save(commit=False)
                            project_to_delete.delete()
                            

                    for skill in skills_formset:
                        if skill.is_valid():
                            if skill.cleaned_data:
                                #****I may need to add 'user', etc.
                                name = skill.cleaned_data['name'].lower()
                                if name.strip() == "":
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
                                    
                                    final_user_profile.skills.add(skill_replace)
                                    print("*****************saved the skill.")
                                    
                    for skill in skills_formset.deleted_forms:
                        print("*****************got past the .deleted_forms.")
                        if skill.is_valid():
                            skill_remove = skill.save()
                            final_user_profile.skills.remove(skill_remove)
                            print("*****************removed the skill.")

                    messages.success(request, 'Your profile is updated!')
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
    my_outside_projects = models.OutsideProject.objects.filter(creator=request.user)
    positions = models.Position.objects.filter(position_filled_user=request.user)
    return render(request, 'profile.html', {'profile': profile, 'positions': positions, 'my_projects': my_projects, 'my_outside_projects': my_outside_projects})



@login_required
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
def applications(request, applications="All Applications", project="All Projects", need="All Needs", action=False, app_pk=False):
    applications=applications
    project=project
    need=need
    # for the slug_url anchor to my profile. 
    profile = models.Profile.objects.get(user=request.user)

    if action:
        if app_pk:
            app_to_accept = models.Application.objects.get(id=app_pk)
            if action == "accepted":
                app_to_accept.accepted = True
                app_to_accept.rejected = False
                app_to_accept.position.position_filled_user = app_to_accept.person_applying
                app_to_accept.position.save()
                print("************** got past the position_filled_user")
                app_to_accept.save()

                models.Notification.objects.create(
                    person_notifying = app_to_accept.person_applying,
                    description = "Your application '{}' for project '{}' has been approved. You got the job!".format(
                        app_to_accept.position.position_name, app_to_accept.position.project.project_name),
                    )
                messages.success(request, "{} application for {} accepted.".format(app_to_accept.person_applying.profile_user.name, app_to_accept.position.position_name))

            elif action == "rejected":
                app_to_accept.rejected = True
                app_to_accept.accepted = False
                app_to_accept.save()

                models.Notification.objects.create(
                    person_notifying = app_to_accept.person_applying,
                    description = "Your application '{}' for project '{}' has been denied".format(
                        app_to_accept.position.position_name, app_to_accept.position.project.project_name),
                    )
                messages.success(request, "{} application for {} rejected.".format(app_to_accept.person_applying.profile_user.name, app_to_accept.position.position_name))

            elif action == "undo":
                app_to_accept.rejected = False
                if app_to_accept.accepted == True:
                    app_to_accept.position.position_filled_user = None
                    app_to_accept.position.save()
                    app_to_accept.accepted = False
                    app_to_accept.save()

                models.Notification.objects.create(
                    person_notifying = app_to_accept.person_applying,
                    description = "Your application '{}' for project '{}' has been changed to undecided.".format(
                        app_to_accept.position.position_name, app_to_accept.position.project.project_name),
                    )
                messages.success(request, "{} application for {} changed to undecided.".format(app_to_accept.person_applying.profile_user.name, app_to_accept.position.position_name))

    all_applications = models.Application.objects.filter(
        position__project__creator=request.user)

    if all_applications:

        #************ filter the applications
        if applications == "All Applications":
            # getting only the applications that haven't been rejected or accepted
            all_applications = all_applications.filter(accepted=False, rejected=False)
        if applications == "New Applications":
            # getting only the applications that haven't been rejected or accepted
            all_applications = all_applications.filter(
                accepted=False,
                rejected=False,
                applied_date__gte=timezone.now().date() - timedelta(days=7))
        elif applications == "Accepted":
            all_applications = all_applications.filter(accepted=True)
        elif applications == "Rejected":
            all_applications = all_applications.filter(rejected=True)

        #************ filter project
        if project != "All Projects":
            all_applications = all_applications.filter(position__project__project_name=project)

        #************* filter need
        if need != "All Needs":
            all_applications = all_applications.filter(position__position_name__icontains=need,
                position__position_description__icontains=need)

    all_projects = models.Project.objects.filter(creator=request.user)

    all_needs = set()
    
    more_needs = models.Position.objects.filter(project__creator=request.user)
    if more_needs:
        for my_need in more_needs:
            all_needs.add(my_need.position_name)
    all_needs = list(all_needs)
    all_needs.insert(0, "All Needs")
    statuses = ["All Applications", "New Applications", "Accepted", "Rejected"]

    return render(request, 'applications.html', {
        'applications': applications, "project": project, "need": need, 
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

@login_required
def notifications(request):
    my_notifications = models.Notification.objects.order_by('-id').filter(person_notifying=request.user)
    return render(request, 'notifications.html', {'my_notifications': my_notifications})



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

