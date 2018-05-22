from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static 

from . import views


app_name = 'social'

urlpatterns = [
	url(r'^$', views.index, name='home'),
    url(r'^(?P<need>[-\w]+)/$', views.index, name='home_need'),
    url(r'^search$', views.search, name='search'),
    url(r'^project_new$', views.project_new, name='project_new'),
    url(r'^project_edit/(?P<url_slug>[-\w]+)/$', views.project_edit, name='project_edit'),
    url(r'^project/(?P<url_slug>[-\w]+)/$', views.project, name='project'),
    url(r'^project/delete/(?P<url_slug>[-\w]+)/$', views.project_delete, name='project_delete'),

    url(r'^profile_edit$', views.profile_edit, name='profile_edit'),
    url(r'^profile/(?P<url_slug>[-\w]+)/$', views.profile, name='profile'),
    url(r'^applications/$', views.applications, name='applications'),
    url(r'^applications/(?P<applications>[-\w]+)/(?P<project>[-\w]+)/(?P<need>[-\w]+)/$', views.applications, name='applications'),
    url(r'^search/(?P<need>[-\w]+)/$', views.search, name='search'),

    url(r'^practice$', views.practice, name='practice'),

    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
