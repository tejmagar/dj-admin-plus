from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelChoiceField, ImageField, ModelMultipleChoiceField, widgets

from dj_admin_plus.widgets import DJFileInput


def get_form_class(model_admin, request, obj=None, change=False):
    if isinstance(model_admin, UserAdmin):
        if change:
            user_admin = UserAdmin(get_user_model(), admin.site)
            return user_admin.get_form(request, obj=obj, change=change)
        else:
            return model_admin.get_form(request, change=change)

    return model_admin.get_form(request, change=change)


# noinspection PyProtectedMember
def modify_model_choice_field(field):
    choices = [(obj.pk, str(obj)) for obj in field._queryset]

    # Modify form widgets
    if isinstance(field, ModelMultipleChoiceField):
        field.widget = widgets.SelectMultiple(choices=choices)
    else:
        field.widget = widgets.Select(choices=choices)


# noinspection PyProtectedMember
def update_form_widgets(form):
    for attrs in form:
        field = attrs.field
        field.label_suffix = ''  # Remove colon from labels

        if isinstance(field, ModelChoiceField):
            modify_model_choice_field(field)

        if isinstance(field, ImageField):
            field.widget = DJFileInput(attrs=field.widget.attrs, image_preview=True)

    return form
