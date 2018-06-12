"""Tests for the project."""

from django.test import TestCase, Client
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from . import models
from . import forms

one_user = {
    "email": "123@gmail.com",
    "password": "123ABC!@#"
}

# need to manually add 'creator' (user)
one_project = {
    "project_name": "My project",
    "description": "LJSDLFJlsjdflasjdfljasldffjf",
    "project_timeline": "6 months",
    "application_requirements": "Must come to headquarters",
    "url_slug": "my_project"
}

# need to manually add 'creator' (user)
one_outsideproject = {
    "project_name": "My Website",
    "url": "www.google.com"
}

# need to manually create 'user'
one_profile = {
    "name": "Michael Jordan",
    "description": "JKlkjjsdlfk sldjf lsdfkj",
    "url_slug": "michael_jordan"
}

# need to manually create 'position_filled_user' and
# 'project'
one_position = {
    "position_name": "Designer",
    "position_description": "LKJD sljflsdfj",
    "hours_per_week": 40,
}


######## testing the models.py
class UserModelTest(TestCase):
    """Testing the User model."""
    def test_user(self):
        first_user = models.User.objects.create_user(**one_user)
        self.assertTrue(models.User.objects.first())
        self.assertEqual(first_user.email, "123@gmail.com")

    def test_user_fail(self):
        with self.assertRaises(ValueError):
            models.User.objects.create_user(email="1234@gmail.com")


class SkillModelTest(TestCase):
    """Testing the Skill model."""
    def test_skill(self):
        models.Skill.objects.create(
            name="Designer")
        skill_1 = models.Skill.objects.first()
        self.assertTrue(skill_1)
        self.assertEqual(skill_1.name, "Designer")

    def test_skill_fail(self):
        with self.assertRaises(AttributeError):
            models.SKill.objects.create()


class ProjectModelTest(TestCase):
    """Testing the Project model."""
    def test_project(self):
        first_user = models.User.objects.create_user(**one_user)

        models.Project.objects.create(
            **one_project,
            creator=first_user)

        project_verify = models.Project.objects.first()
        self.assertTrue(project_verify)
        self.assertEqual(project_verify.project_name, "My project")

    def test_project_fail(self):
        # fail creating a project with no creator.
        with self.assertRaises(IntegrityError):
            models.Project.objects.create(
                **one_project)


class OutsideProject(TestCase):
    """Testing the OutsideProject model."""
    def test_outside_project(self):
        first_user = models.User.objects.create_user(**one_user)

        models.OutsideProject.objects.create(
            **one_outsideproject,
            creator=first_user)
        outside_project1 = models.OutsideProject.objects.first()
        self.assertTrue(outside_project1)
        self.assertEqual(outside_project1.project_name, "My Website")

    def test_outside_project_fail(self):
        with self.assertRaises(IntegrityError):
            models.OutsideProject.objects.create(
                **one_outsideproject)


class ProfileModelTest(TestCase):
    """Testing the Profile model."""
    def test_profile_model(self):
        first_user = models.User.objects.create_user(**one_user)

        models.Profile.objects.create(
            **one_profile,
            user=first_user)

        profile1 = models.Profile.objects.first()
        self.assertEqual(profile1.name, "Michael Jordan")

    def test_profile_model_fail(self):
        with self.assertRaises(IntegrityError):
            models.Profile.objects.create(
                **one_profile)


class PositionModelTest(TestCase):
    """Testing the Position model."""
    def test_position_model(self):
        first_user = models.User.objects.create_user(**one_user)

        project1 = models.Project.objects.create(
            **one_project,
            creator=first_user)

        models.Position.objects.create(
            **one_position,
            project=project1,
            position_filled_user=first_user)

        position1 = models.Position.objects.first()
        self.assertEqual(position1.position_name, "Designer")

    def position_model_test_fail(self):
        with self.assertRaises(IntegrityError):
            models.Position.objects.create(**one_position)


class ApplicationModelTest(TestCase):
    """Testing the Application model."""
    def test_application_model(self):
        first_user = models.User.objects.create_user(**one_user)

        project1 = models.Project.objects.create(
            **one_project,
            creator=first_user)

        position1 = models.Position.objects.create(
            **one_position,
            project=project1,
            position_filled_user=first_user)

        models.Application.objects.create(
            position=position1,
            person_applying=first_user)

        application1 = models.Application.objects.first()
        self.assertTrue(application1.position, position1)
        self.assertTrue(application1.person_applying, first_user)

        with self.assertRaises(IntegrityError):
            models.Application.objects.create(
                position=position1,
                person_applying=first_user)


######## testing the forms.py
class UserCreateFormTest(TestCase):
    """Testing the UserCreate form."""
    def test_usercreateform(self):
        form = forms.UserCreateForm(data={
            'email': 'email1@gmail.com',
            'password1': '123!@#abc',
            'password2': '123!@#abc'})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('email'), 'email1@gmail.com')
        self.assertNotEqual(form.cleaned_data.get('email'), 'email2@gmail.com')

    def test_usercreateform_fail(self):
        form = forms.UserCreateForm(data={
            'email': 'email1',
            'password1': '123!@#abc',
            'password2': '123!@#abc'})

        self.assertFalse(form.is_valid())

    def test_usercreateform_fail2(self):
        form = forms.UserCreateForm(data={
            'email': 'email1@gmail.com',
            'password1': '123!@#abc',
            'password2': '146!@#abc'})

        self.assertFalse(form.is_valid())


class ProfileFormTest(TestCase):
    """Testing the Profile form."""
    def test_profileform(self):

        form = forms.ProfileForm(data={
            "name": "Michael Jordan",
            "description": "LJsljdf sldjjfsldf"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('name'), "Michael Jordan")

    def test_profileform_fail(self):
        form = forms.ProfileForm(data={
            "name": "Michael Jordan"})

        self.assertFalse(form.is_valid())


class SkillFormTest(TestCase):
    """Testing the Skill form."""
    def test_skillform(self):
        form = forms.SkillForm(data={
            "name": "designer"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('name'), "designer")


class ProjectFormTest(TestCase):
    """Testing the Project form."""
    def test_projectform(self):
        form = forms.ProjectForm(data={
            "project_name": "Networking website",
            "description": "LKs alsdfalsdkfj asdlf",
            "project_timeline": "6 months",
            "application_requirements": "Must live in state"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('project_name'),
                         'Networking website')

    def test_projectform_fail(self):
        form = forms.ProjectForm(data={
            "description": "LKs alsdfalsdkfj asdlf",
            "project_timeline": "6 months",
            "application_requirements": "Must live in state"})

        self.assertFalse(form.is_valid())


class PostionFormTest(TestCase):
    """Testing the Position form."""
    def test_positionform(self):
        form = forms.PositionForm(data={
            "position_name": "designer",
            "position_description": "LKJ slsldfj asld",
            "hours_per_week": 10})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('position_name'), 'designer')

    def test_positionform_fail(self):
        form = forms.PositionForm(data={
            "position_name": "designer",
            "position_description": "LKJ slsldfj asld"})

        self.assertFalse(form.is_valid())


class ProfileMyProjectsFormTest(TestCase):
    """Testing the ProfileMyProjects form."""
    def test_profilemyprojectsformtest(self):
        form = forms.ProfileMyProjectsForm(data={
            "project_name": "Social Media",
            "url": "www.google.com"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('project_name'), 'Social Media')

    def test_profilemyprojectsformtest_fail(self):
        form = forms.ProfileMyProjectsForm(data={
            "url": "www.google.com"})

        self.assertFalse(form.is_valid())

    def test_profilemyprojectsformtest_fail2(self):
        form = forms.ProfileMyProjectsForm(data={
            "project_name": "Social Media"})

        self.assertFalse(form.is_valid())


################# testing the views.py
class ProfileNewViewTest(TestCase):
    """Testing the profile_new view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

    def test_profile_new_get(self):
        response = self.client.get(reverse('base:profile_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_edit.html')
        self.assertContains(response, 'Profile')


class ProfileEditViewTest(TestCase):
    """Testing the profile_edit view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(
            **one_profile,
            user=first_user)

    def test_profile_edit_get(self):
        response = self.client.get(reverse('base:profile_edit'))
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):
    """Testing the profile view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(
            **one_profile,
            user=first_user)

    def test_profile_view(self):
        profile_1 = models.Profile.objects.first()
        response = self.client.get(reverse('base:profile',
                                           args=[profile_1.url_slug]))
        self.assertEqual(response.status_code, 200)


class ProjectNewViewTest(TestCase):
    """Testing the project_new view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

    def test_project_new_get(self):
        response = self.client.get(reverse('base:project_new'))
        self.assertEqual(response.status_code, 200)


class ProjectEditViewTest(TestCase):
    """Testing the project_edit view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Project.objects.create(**one_project, creator=first_user)

    def test_project_edit_get(self):
        project1 = models.Project.objects.first()
        response = self.client.get(reverse('base:project_edit',
                                           args=[project1.url_slug]))
        self.assertEqual(response.status_code, 200)


class ProjectViewTest(TestCase):
    """Testing the project view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(**one_profile, user=first_user)

        models.Project.objects.create(**one_project, creator=first_user)

    def test_project(self):
        project1 = models.Project.objects.first()
        response = self.client.get(reverse('base:project',
                                           args=[project1.url_slug]))
        self.assertEqual(response.status_code, 200)


class IndexViewTest(TestCase):
    """Testing the index view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(**one_profile, user=first_user)

    def test_index(self):
        response = self.client.get(reverse('base:home'))
        self.assertEqual(response.status_code, 200)

    def test_index_2(self):
        response = self.client.get(reverse('base:home_need', args=["designer"]))
        self.assertEqual(response.status_code, 200)


class ProjectDeleteViewTest(TestCase):
    """Testing the project_delete view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(**one_profile, user=first_user)

        models.Project.objects.create(**one_project, creator=first_user)

    def test_project_delete(self):
        proj_1 = models.Project.objects.first()
        response = self.client.get(reverse('base:project_delete',
                                           args=[proj_1.url_slug]))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            models.Project.objects.get(project_name="My project")


class SearchViewTest(TestCase):
    """Testing the search view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

    def test_search(self):
        response = self.client.get('%s?q=Abra' % reverse('base:search'))
        self.assertEqual(response.status_code, 200)


class ApplicationsViewTest(TestCase):
    """Testing the applications view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

        models.Profile.objects.create(**one_profile, user=first_user)

    def test_applications(self):
        response = self.client.get(reverse('base:home_applications'))
        self.assertEqual(response.status_code, 200)


class LogOutViewTest(TestCase):
    """Testing the logout view."""
    def setUp(self):
        first_user = models.User.objects.create_user(**one_user)
        self.client = Client()
        self.client.force_login(first_user)

    def test_logout(self):
        response = self.client.get(reverse('loggedout'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('login.html')
