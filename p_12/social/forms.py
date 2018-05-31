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


class ProfileForm(forms.ModelForm):
    class Meta:
        fields = ("name", "description", "image")
        model = models.Profile

class SkillForm(forms.ModelForm):
    name = forms.CharField(required=False)
    class Meta:
        fields = ("name",)
        model = models.Skill 



class ProjectForm(forms.ModelForm):
    
    class Meta:
        fields = (
            "project_name", "description", "project_timeline", "application_requirements")
        model = models.Project


class PositionForm(forms.ModelForm):
    class Meta:
        fields = (
            "position_name", "position_description")
        model = models.Position





        
class ProfileMyProjectsForm(forms.ModelForm):
    project_name = forms.CharField(max_length=255, required=False)
    url = forms.URLField(max_length=255, required=False)
    class Meta:
        fields = (
            "project_name",
            "url")
        model = models.OutsideProject

    def clean(self):
        cleaned_data = super().clean()
        p_name = cleaned_data.get("project_name")
        the_url = cleaned_data.get("url")

        if p_name == "":
            if the_url != "":
                raise forms.ValidationError(
                    "Did not fill out the project name"
                )

        if the_url == "":
            if p_name != "":
                raise forms.ValidationError(
                    "Did not fill out the project's url"
                )


        


class ApplicationForm(forms.ModelForm):
    class Meta:
        fields = ('accepted',)
        model = models.Application