from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from PIL import Image


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")

        user_obj = self.model(
            email = self.normalize_email(email)
        )
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True
            )
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_admin=True
            )
        return user



class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    active = models.BooleanField(default=True) #can login
    staff = models.BooleanField(default=False) #staff user non superuser
    admin = models.BooleanField(default=False) #superuser

    USERNAME_FIELD = 'email'
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active





class Skill(models.Model):
    name = models.CharField(max_length=255)
    



    

class Project(models.Model):
    project_name = models.CharField(max_length=255,)
    creator = models.ForeignKey(User, on_delete=True, related_name='project_owner')
    description = models.TextField()
    project_timeline = models.TextField()
    application_requirements = models.TextField()
    url_slug = models.SlugField(unique=True)

class OutsideProject(models.Model):
    project_name = models.CharField(max_length=255,)
    creator = models.ForeignKey(User, on_delete=True, related_name='outsideproject_owner')
    url = models.URLField(max_length=200)
    


class Profile(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to=settings.MEDIA_ROOT, blank=True, default="")
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

    class Meta:
        unique_together = ('position', 'person_applying')


class Notification(models.Model):
    description = models.CharField(max_length=255)
    person_notifying = models.ForeignKey(User, on_delete=True, related_name="notifications")
    time_of_notification = models.DateField(auto_now_add=True)
    already_seen = models.BooleanField(default=False)