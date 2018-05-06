from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 

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