from django import template
from django.contrib.auth import get_user_model
from django.urls import reverse

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


# noinspection PyProtectedMember
@register.simple_tag
def user_info_change_url(user):
    user_model = get_user_model()
    app_label = user_model._meta.app_label
    model_name = user_model._meta.model_name

    return reverse('change_model_view', kwargs={
        'app_label': app_label,
        'model_name': model_name,
        'pk': user.pk
    })

