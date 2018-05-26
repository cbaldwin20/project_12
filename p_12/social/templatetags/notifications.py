from django import template

from social import models

register = template.Library() 

@register.inclusion_tag('notification_icon.html')
def is_notify():
	to_notify = False 
	try:
		notification = models.Notification.objects.get()
	except models.Notification.DoesNotExist:
		to_notify = False
	else:
		if notification.already_seen:
			to_notify = False
		else:
			to_notify = True

	return {'to_notify': to_notify}

@register.simple_tag
def notify_clear():
	notifications = models.Notification.objects.filter(already_seen=False)
	notifications.update(already_seen=True)