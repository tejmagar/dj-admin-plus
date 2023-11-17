from django import template
from django.forms import widgets

from .. import navigation

register = template.Library()


@register.inclusion_tag(takes_context=True, filename='dj_admin_plus/sidebar.html')
def sidebar_navigations(context):
    return {
        'navigations': navigation.default_manager.get_items(context.request)
    }


@register.filter
def value_from_field(model, field_name):
    return getattr(model, field_name)


@register.simple_tag
def get_form_field_from_name(form, field_name):
    try:
        field = form[field_name]
        return field
    except:
        return None


@register.simple_tag
def field_instance_of(field):
    pass
