# app/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def dict_key(d, key):
    return d.get(key)

from django import template

register = template.Library()

@register.filter
def activity_type_color(activity):
    if activity.type == 'login':
        return 'success'
    elif activity.type == 'logout':
        return 'secondary'
    elif activity.type == 'test':
        return 'info'
    elif activity.type == 'error':
        return 'danger'
    else:
        return 'primary'
