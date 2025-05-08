{% load widget_tweaks %}

from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, SafeString):
        return field
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='add_placeholder')
def add_placeholder(field, placeholder_text):
    if isinstance(field, SafeString):
        return field
    return field.as_widget(attrs={'placeholder': placeholder_text})
