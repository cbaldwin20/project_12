from django import template

from social import models

register = template.Library() 

@register.inclusion_tag('notification_icon.html')
def is_notify(user):
	notification = models.Notification.objects.filter(person_notifying=user, already_seen=False)
	if notification:
		to_notify = True
		count = notification.count()
	else:
		to_notify = False
		count = 0

	return {'to_notify': to_notify, 'count': count }

@register.simple_tag
def notify_clear(user):
	notifications = models.Notification.objects.filter(person_notifying=user, already_seen=False)
	notifications.update(already_seen=True)

@register.simple_tag
def did_apply(applications, user):
	is_user_in = []
	for application in applications:
		is_user_in.append(application.person_applying)
	if user in is_user_in:
		return True
	else:
		return False




