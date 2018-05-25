from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image




class Skill(models.Model):
    name = models.CharField(max_length=255)
    



    

class Project(models.Model):
    project_name = models.CharField(max_length=255,)
    creator = models.ForeignKey(User, on_delete=True, related_name='project_owner')
    description = models.TextField()
    project_timeline = models.TextField()
    application_requirements = models.TextField()
    url_slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)


class Profile(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to=settings.MEDIA_ROOT, default="")
    user = models.OneToOneField(User, on_delete=True, related_name='profile_user')
    projects = models.ManyToManyField(Project, related_name='user_projects')
    skills = models.ManyToManyField(Skill, related_name='user_skills')
    url_slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        # this is required when you override save functions
        super(Profile, self).save(*args, **kwargs)

        if self.image:
            image = Image.open(self.image)
            i_width, i_height = image.size
            max_size = (300, 400)

            if i_width > 200:
                image.thumbnail(max_size, Image.ANTIALIAS)
                image.save(self.image.path)


class Position(models.Model):
    position_name = models.CharField(max_length=255)
    position_description = models.TextField()
    project = models.ForeignKey(Project, on_delete=True, related_name='project_positions')
    position_filled_user = models.ForeignKey(User, on_delete=True, related_name='my_position_for_project', blank=True,
    null=True,)


class SkillDescriptions(models.Model):
    description = models.TextField()
    skill = models.ForeignKey(Skill, on_delete=True, related_name='skill_description')
    project_owner = models.ForeignKey(User, on_delete=True, related_name='user_of_description')



class Application(models.Model):
    position = models.ForeignKey(Position, on_delete=True, related_name='position_applications')
    person_applying = models.ForeignKey(User, on_delete=True, related_name='applications')
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    applied_date = models.DateField(auto_now_add=True)