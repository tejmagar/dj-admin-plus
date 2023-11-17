import enum
from abc import ABC
from typing import Type

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model, authenticate, login
from django.core.paginator import Paginator
from django.db.models import Model
from django.http import Http404, HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import safe
from django.urls import reverse
from django.views import View

from dj_admin_plus import utils, navigation
from dj_admin_plus.utils import update_form_widgets
from dj_admin_plus.mixins import AdminLoginRequiredMixin

from .forms import AdminLoginForm


# Create your views here.

class AdminLoginView(View):

    def get_username_field(self):
        user_model = get_user_model()
        return getattr(user_model, user_model.USERNAME_FIELD).field

    def get(self, request):
        return render(request, 'dj_admin_plus/auth/login.html', {
            'username_field': self.get_username_field(),
        })

    def post(self, request):
        redirect_to = request.GET.get('next', reverse('dj_admin_plus'))

        form = AdminLoginForm(data=request.POST)

        if form.is_valid():
            credentials = {
                'username': form.cleaned_data['login'],
                'password': form.cleaned_data['password']
            }
            print(credentials)
            user = authenticate(request, **credentials)
            if user:
                login(request, user)
                return HttpResponseRedirect(redirect_to)

            form.add_error(None, 'Invalid email or password')

        print(form.errors)
        return render(request, 'dj_admin_plus/auth/login.html', {
            'username_field': self.get_username_field(),
            'form': form
        })


# noinspection PyProtectedMember
class AdminView(AdminLoginRequiredMixin, View):
    def get(self, request, **kwargs):
        navigation_manager = navigation.default_manager

        if len(navigation_manager.items) == 0:
            # The navigation manager has no items, so display standard tutorial page.
            return render(request, 'dj_admin_plus/tutorial.html')

        """
        Check if user has set the entry view while user access the admin page.
        """

        entry_navigation = navigation_manager.entry_view_navigation

        if entry_navigation and entry_navigation.view:
            # Check whether user has permission to access this page or not.

            if entry_navigation.permission_check:
                has_permission = entry_navigation.permission_check(request)

                if not has_permission:
                    return HttpResponseForbidden()

            entry_view = entry_navigation.view

            if isinstance(entry_view, View):
                return entry_view.as_view(request, **kwargs)

            # Presuming the attribute value is callable
            return entry_view(request, **kwargs)

        # No entry view is set, choose first url from navigation items

        # Check permission for first navigation item
        navigation_item = navigation_manager.items[0]

        if navigation_item.permission_check:
            has_permission = entry_navigation.permission_check(request)

            if not has_permission:
                return HttpResponseForbidden()

        # Handle fallback navigation if url
        if navigation_manager.select_fallback_first and navigation_item.url:
            return redirect(navigation_item.url)

        # Handle fallback navigation if model
        if navigation_manager.select_fallback_first and navigation_item.model:
            app_label = navigation_item.model._meta.app_label
            model_name = navigation_item.model._meta.model_name

            return redirect(reverse('model_view', kwargs={
                'app_label': app_label,
                'model_name': model_name
            }))

        return render(request, 'dj_admin_plus/setup-default-view.html')


class Permission(enum.Enum):
    VIEW = 'view'
    ADD = 'add'
    CHANGE = 'change'
    DELETE = 'delete'


class BaseModelView(AdminLoginRequiredMixin, View, ABC):
    def get_app_label_and_model_name(self, **kwargs):
        app_label = kwargs.get('app_label')
        model_name = kwargs.get('model_name')
        return app_label, model_name

    def get_model_class(self, app_label, model_name) -> Type[Model]:
        try:
            return apps.get_model(app_label, model_name=model_name)
        except LookupError:
            raise Http404(f'Model {model_name} for app name {app_label} does not exist.')

    def has_model_permission(self, user, app_label, model_name, permission: Permission):
        return user.has_perm(f'{app_label}.{permission}_{model_name}')

    def has_navigation_permission(self, request, app_label, model_name) -> bool:
        """
        Since Base model view deals with only model based view, we will query all the matching model.

        If there are multiple navigation set for same model, it will call permission check callback for all those
        navigations.
        """

        model_class = self.get_model_class(app_label, model_name)

        matched_navigations = navigation.default_manager.get_navigations_by_model_class(model_class)

        for _navigation in matched_navigations:
            if _navigation.permission_check:
                check = _navigation.permission_check(request)

                if not check:
                    return False

        return True

    def validate_permission_or_raise_404(self, request, app_label, model_name,
                                         permission: Permission):
        has_view_permission = self.has_model_permission(request.user, app_label, model_name, permission)

        if not has_view_permission or not self.has_navigation_permission(request, app_label, model_name):
            raise Http404()

    def get_model_admin(self, model_class):
        # noinspection PyProtectedMember
        return admin.site._registry[model_class]


class ModelView(BaseModelView):

    def bool_to_symbol(self, value):
        if value:
            value = '<span style="color:green; font-size: 20px;">✓</span>'
        else:
            value = '<span style="color:red; font-size: 20px;">✗</span>'

        return safe(value)

    def get_value_from_field(self, model_admin, item, display_item):
        if hasattr(item, display_item):
            func = getattr(item, display_item)

            if callable(func):
                value = func()
            else:
                value = func

            if type(value) == bool:
                value = self.bool_to_symbol(value)

            return str(value)

        if hasattr(model_admin, display_item):
            func = getattr(model_admin, display_item)
            value = func(item)

            if type(value) == bool:
                value = self.bool_to_symbol(value)

            return value

        return None

    def construct_items(self, admin_class, object_list, display_items):
        display_objects = []

        for item in object_list:
            record = []

            for display_item in display_items:
                record.append(self.get_value_from_field(admin_class, item, display_item))

            display_objects.append((item.pk, record))

        return display_objects

    # noinspection PyProtectedMember
    def get(self, request, **kwargs):
        app_label, model_name = self.get_app_label_and_model_name(**kwargs)
        self.validate_permission_or_raise_404(request, app_label, model_name, Permission.VIEW)

        model_class = self.get_model_class(app_label, model_name)
        admin_class = self.get_model_admin(model_class).__class__
        list_display = admin_class.list_display

        page_number = request.GET.get('page')
        items = model_class.objects.order_by('-pk').all()
        paginator = Paginator(items, admin_class.list_per_page)
        page = paginator.get_page(page_number)

        model_admin = admin_class(model_class, admin.site)

        items = self.construct_items(model_admin, page.object_list, list_display)
        return render(request, 'dj_admin_plus/view-items.html', {
            'app_label': app_label,
            'model_name': model_name,
            'title': model_class._meta.verbose_name_plural.title(),
            'items': items,
            'default_field_name': model_class._meta.verbose_name.upper(),
            'list_display': list_display
        })


class EditModelView(BaseModelView):
    add_mode = False

    def get_current_fieldsets(self, model_admin, add_mode: bool):
        if add_mode:
            if hasattr(model_admin, 'add_fieldsets'):
                return model_admin.add_fieldsets

        else:
            if hasattr(model_admin, 'fieldsets'):
                return model_admin.fieldsets

        return None

    def get(self, request, **kwargs):
        app_label, model_name = self.get_app_label_and_model_name(**kwargs)
        self.validate_permission_or_raise_404(request, app_label, model_name, Permission.ADD)

        model_class = self.get_model_class(app_label, model_name)
        model_admin = self.get_model_admin(model_class)

        if self.add_mode:
            form_class = utils.get_form_class(model_admin=model_admin, request=request)
            form = form_class()

        else:
            pk = kwargs.get('pk')
            model = get_object_or_404(model_class, pk=pk)

            form_class = utils.get_form_class(model_admin, request=request, obj=model, change=True)
            form = form_class(instance=model)

        form = update_form_widgets(form)
        operation = 'Add' if self.add_mode else 'Change'

        return render(request, 'dj_admin_plus/edit-item.html', {
            'app_label': app_label,
            'model_name': model_name,
            'title': f'{operation} {model_name.lower()}',
            'fieldsets': self.get_current_fieldsets(model_admin, self.add_mode),
            'form': form,
            'add_mode': self.add_mode
        })

    # noinspection PyProtectedMember
    def post(self, request, **kwargs):
        save_and_add_another = request.POST.get('save_and_add_another')
        save_and_continue_editing = request.POST.get('save_and_continue_editing')
        delete = request.POST.get('delete')

        app_label, model_name = self.get_app_label_and_model_name(**kwargs)
        self.validate_permission_or_raise_404(request, app_label, model_name, Permission.ADD)

        model_class = self.get_model_class(app_label, model_name)
        model_admin = self.get_model_admin(model_class)

        if self.add_mode:
            form_class = utils.get_form_class(model_admin, request=request)
            form = form_class(data=request.POST, files=request.FILES)

        else:
            pk = kwargs.get('pk')
            model = get_object_or_404(model_class, pk=pk)

            if delete:
                model.delete()
                return redirect(reverse('model_view', kwargs={
                    'app_label': app_label,
                    'model_name': model_name
                }))

            form_class = utils.get_form_class(model_admin, request=request, obj=model, change=True)
            form = form_class(instance=model, data=request.POST, files=request.FILES)

        if form.is_valid():
            form.save()

            if save_and_add_another:
                return redirect(reverse('add_model_view', kwargs={
                    'app_label': app_label,
                    'model_name': model_name
                }))

            elif save_and_continue_editing:
                return redirect(request.path)

            return redirect(reverse('model_view', kwargs={
                'app_label': app_label,
                'model_name': model_name
            }))

        form = update_form_widgets(form)
        operation = 'Add' if self.add_mode else 'Change'

        return render(request, 'dj_admin_plus/edit-item.html', {
            'app_label': app_label,
            'model_name': model_name,
            'fieldsets': self.get_current_fieldsets(model_admin, self.add_mode),
            'title.html': f'{operation} {model_name.lower()}',
            'form': form,
            'add_mode': self.add_mode
        })
