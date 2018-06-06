from django.test import TestCase
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from . import models
from . import forms

one_user = {
	"email":"123@gmail.com",
	"password":"123ABC!@#"
}

# need to manually add 'creator' (user)
one_project = {
	"project_name":"My project",
	"description":"LJSDLFJlsjdflasjdfljasldffjf",
	"project_timeline":"6 months",
	"application_requirements":"Must come to headquarters",
	"url_slug":"my_project"
}

# need to manually add 'creator' (user)
one_outsideproject = {
	"project_name":"My Website",
	"url":"www.google.com"
}

# need to manually create 'user'
one_profile = {
	"name":"Michael Jordan",
	"description":"JKlkjjsdlfk sldjf lsdfkj",
	"url_slug":"michael_jordan"
}

# need to manually create 'position_filled_user' and
# 'project'
one_position = {
	"position_name":"Designer",
	"position_description":"LKJD sljflsdfj",
	"hours_per_week":40,
}

######## testing the models.py
class UserModelTest(TestCase):
	def test_user(self):
		first_user = models.User.objects.create_user(
		**one_user)

		self.assertTrue(models.User.objects.first())
		self.assertEqual(first_user.email, "123@gmail.com")

	def test_user_fail(self):
		with self.assertRaises(ValueError):
			models.User.objects.create_user(
			email = "1234@gmail.com",
			)


class SkillModelTest(TestCase):
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
	def test_project(self):
		first_user = models.User.objects.create_user(
		**one_user)

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
	def test_outside_project(self):
		first_user = models.User.objects.create_user(
		**one_user)

		models.OutsideProject.objects.create(
			**one_outsideproject,
			creator=first_user,
			)
		outside_project1 = models.OutsideProject.objects.first()
		self.assertTrue(outside_project1)
		self.assertEqual(outside_project1.project_name, "My Website")

	def test_outside_project_fail(self):

		with self.assertRaises(IntegrityError):
			models.OutsideProject.objects.create(
				**one_outsideproject
				)
		
class ProfileModelTest(TestCase):
	def test_profile_model(self):
		first_user = models.User.objects.create_user(
		**one_user)

		models.Profile.objects.create(
			**one_profile,
			user=first_user
			)

		profile1 = models.Profile.objects.first()
		self.assertEqual(profile1.name, "Michael Jordan")

	def test_profile_model_fail(self):
		with self.assertRaises(IntegrityError):
			models.Profile.objects.create(
			**one_profile)

class PositionModelTest(TestCase):
	def test_position_model(self):
		first_user = models.User.objects.create_user(
		**one_user)

		project1 = models.Project.objects.create(
			**one_project,
			creator = first_user,
			)

		models.Position.objects.create(
			**one_position,
			project=project1,
			position_filled_user=first_user,
			)

		position1 = models.Position.objects.first()
		self.assertEqual(position1.position_name, "Designer")

	def position_model_test_fail(self):
		with self.assertRaises(IntegrityError):
			models.Position.objects.create(
			**one_position
			)


class ApplicationModelTest(TestCase):
	def test_application_model(self):
		first_user = models.User.objects.create_user(
		**one_user)

		project1 = models.Project.objects.create(
			**one_project,
			creator = first_user,
			)

		position1 = models.Position.objects.create(
			**one_position,
			project=project1,
			position_filled_user=first_user,
			)

		models.Application.objects.create(
			position=position1,
			person_applying=first_user,
			)

		application1 = models.Application.objects.first()
		self.assertTrue(application1.position, position1)
		self.assertTrue(application1.person_applying, first_user)

		with self.assertRaises(IntegrityError):
			models.Application.objects.create(
				position=position1,
				person_applying=first_user,
				)

######## testing the forms.py

class UserCreateFormTest(TestCase):
	def test_usercreateform(self):
		form = forms.UserCreateForm(data={
			'email': 'email1@gmail.com',
			'password1': '123!@#abc',
			'password2': '123!@#abc'
			})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('email'), 'email1@gmail.com')
		self.assertNotEqual(form.cleaned_data.get('email'), 'email2@gmail.com')

	def test_usercreateform_fail(self):
		form = forms.UserCreateForm(data={
			'email': 'email1',
			'password1': '123!@#abc',
			'password2': '123!@#abc'
			})

		self.assertFalse(form.is_valid())

	def test_usercreateform_fail2(self):
		form = forms.UserCreateForm(data={
			'email': 'email1@gmail.com',
			'password1': '123!@#abc',
			'password2': '146!@#abc'
			})

		self.assertFalse(form.is_valid())


class ProfileFormTest(TestCase):
	def test_profileform(self):

		form = forms.ProfileForm(data={
			"name": "Michael Jordan",
			"description": "LJsljdf sldjjfsldf",
			})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('name'), "Michael Jordan")

	def test_profileform_fail(self):
		form = forms.ProfileForm(data={
			"name": "Michael Jordan",
			})
		self.assertFalse(form.is_valid())

class SkillFormTest(TestCase):
	def test_skillform(self):
		form = forms.SkillForm(data={
			"name": "designer"
			})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('name'), "designer")

class ProjectFormTest(TestCase):
	def test_projectform(self):
		form = forms.ProjectForm(data={
			"project_name": "Networking website",
			"description": "LKs alsdfalsdkfj asdlf",
			"project_timeline": "6 months",
			"application_requirements": "Must live in state"
			})	

		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('project_name'), 'Networking website')

	def test_projectform_fail(self):
		form = forms.ProjectForm(data={
			"description": "LKs alsdfalsdkfj asdlf",
			"project_timeline": "6 months",
			"application_requirements": "Must live in state"
			})	

		self.assertFalse(form.is_valid())

class PostionFormTest(TestCase):
	def test_positionform(self):
		form = forms.PositionForm(data={
			"position_name": "designer",
			"position_description": "LKJ slsldfj asld",
			"hours_per_week": 10
			})

		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('position_name'), 'designer')

	def test_positionform_fail(self):
		form = forms.PositionForm(data={
			"position_name": "designer",
			"position_description": "LKJ slsldfj asld",
			})

		self.assertFalse(form.is_valid())


class ProfileMyProjectsFormTest(TestCase):
	def test_profilemyprojectsformtest(self):
		form = forms.ProfileMyProjectsForm(data={
			"project_name": "Social Media",
			"url": "www.google.com"
			})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('project_name'), 'Social Media')

	def test_profilemyprojectsformtest_fail(self):
		form = forms.ProfileMyProjectsForm(data={
			"url": "www.google.com"
			})
		self.assertFalse(form.is_valid())

	def test_profilemyprojectsformtest_fail2(self):
		form = forms.ProfileMyProjectsForm(data={
			"project_name": "Social Media"
			})
		self.assertFalse(form.is_valid())


class ApplicationFormTest(TestCase):
	def test_applicationformtest(self):
		form = forms.ApplicationForm(data={
			"accepted": True
			})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data.get('accepted'), True)