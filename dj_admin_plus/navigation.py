import dataclasses
from abc import ABC
from copy import deepcopy
from typing import List, Optional, Callable, Type, Union

from django.db.models import Model
from django.urls import reverse, reverse_lazy
from django.views import View


@dataclasses.dataclass
class Navigation:
    _id: str
    title: str
    icon_class: Optional[str] = None
    model: Optional[Type[Model]] = None
    view: Optional[Union[Callable, Type[View]]] = None
    url: Optional[str] = None
    children: Optional[List['Navigation']] = None
    permission_check: Callable = None
    show: bool = True
    selected: bool = False

    def __has_permission__(self, request) -> bool:
        if self.permission_check:
            return self.permission_check(request)

        return True

    def setup(self, request):
        """
        Called from NavigationManager class.
        """

        if self.model:
            # noinspection PyProtectedMember
            self.url = reverse("model_view",
                               kwargs={
                                   'app_label': self.model._meta.app_label,
                                   'model_name': self.model._meta.model_name.lower()
                               })

        self.show = self.__has_permission__(request)


# noinspection PyProtectedMember
class NavigationManager(ABC):
    items: List[Navigation] = []
    entry_view_navigation: Optional[Navigation] = None  # Navigation with view attribute specified
    select_fallback_first: bool = False

    def setup_entry_view(self):
        """
        Selects default view to what ever comes first which has `item.view` attribute set to show for admin entry.

        Used reverse_lazy because Django was unable to found the reverse url.
        """

        for item in self.items:
            if item.view:
                self.entry_view_navigation = item
                try:
                    item.url = reverse_lazy('dj_admin_plus')
                except Exception as e:
                    raise Exception('Looks like dj_admin_plus is not included in urls.py')

            if not item.children:
                continue

            for child in item.children:
                if child.view:
                    self.entry_view_navigation = child
                    item.url = reverse_lazy('dj_admin_plus')
                    break

    def is_selected(self, request, item, match_sub_url=False):
        if item.model:
            app_label = item.model._meta.app_label
            model_name = item.model._meta.model_name.lower()

            reverse_url = reverse('model_view', kwargs={
                'app_label': app_label,
                'model_name': model_name
            })

            if match_sub_url and request.path.startswith(reverse_url):
                return True

        return item.url == request.path

    def setup_navigations(self, items, request):
        for item in items:
            item.setup(request)
            item.selected = self.is_selected(request, item, match_sub_url=True)

            children = item.children
            if children:
                for child in item.children:
                    child.setup(request)
                    child.selected = self.is_selected(request, child)

                    # Select parent navigation also, if child path matches current url.
                    if child.selected:
                        item.selected = True

    def get_items(self, request):
        """
        Copies the navigation structure to prevent showing same referenced values.

        After copying, depending on request it will change navigation instance `show` attribute
        to True or False depending on `permission_check` callback.
        """

        items = deepcopy(self.items)
        self.setup_navigations(items, request)
        return items

    def __get_recursive_navigations__(self, navigations: List[Navigation], tmp_list) -> None:
        if not navigations:
            return

        for navigation in navigations:
            tmp_list.append(navigation)

            children = navigation.children

            if children:
                self.__get_recursive_navigations__(children, tmp_list)

    def get_all_navigations(self):
        tmp_navigations = []
        self.__get_recursive_navigations__(self.items, tmp_navigations)
        return tmp_navigations

    def get_navigations_by_model_class(self, model_class: Type[Model]):
        matched_navigations = []
        for navigation in self.get_all_navigations():
            if navigation.model == model_class:
                matched_navigations.append(navigation)

        return matched_navigations


class DefaultManager(NavigationManager):
    pass


default_manager = DefaultManager()


def register(navigations: List[Navigation], select_fallback_first: Optional[bool] = False):
    default_manager.items = navigations
    default_manager.select_fallback_first = select_fallback_first
    default_manager.setup_entry_view()
