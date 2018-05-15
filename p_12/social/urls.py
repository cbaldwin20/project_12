from django.conf.urls import url, include
from . import views

app_name = 'social'

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search$', views.search, name='search'),
    url(r'^project_new$', views.project_new, name='project_new'),
    url(r'^project_edit$', views.project_edit, name='project_edit'),
    url(r'^project$', views.project, name='project'),
    url(r'^profile_edit$', views.profile_edit, name='profile_edit'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^applications$', views.applications, name='applications'),

    
    

]
