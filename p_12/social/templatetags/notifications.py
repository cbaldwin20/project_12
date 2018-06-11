"""The code to alert for notifications."""

from django import template

from social import models

register = template.Library()


@register.inclusion_tag('notification_icon.html')
def is_notify(user):
	"""Find if there are any notifications for user."""
	notification = models.Notification.objects.filter(
		person_notifying=user,
		already_seen=False)
	if notification:
		to_notify = True
		count = notification.count()
	else:
		to_notify = False
		count = 0

	return {'to_notify': to_notify, 'count': count}


@register.simple_tag
def notify_clear(user):
	"""Mark all notifications as 'seen' once they've been seen"""
	notifications = models.Notification.objects.filter(
		person_notifying=user,
		already_seen=False)
	notifications.update(already_seen=True)


@register.simple_tag
def did_apply(applications, user):
	"""
	Find if user has applied to position, so can make it
	so they can't apply twice.
	"""
	is_user_in = []
	for application in applications:
		is_user_in.append(application.person_applying)
	if user in is_user_in:
		return True
	else:
		return False
