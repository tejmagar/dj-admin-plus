from django.db import models

from .widgets import TinyMCE


class HTMLField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.attrs = kwargs.get('attrs')
        if self.attrs:
            kwargs.pop('attrs')

        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        if self.attrs:
            widget_attrs = kwargs.get('attrs')
        else:
            widget_attrs = {'rows': 4, 'cols': 40}

        widget = TinyMCE(attrs=widget_attrs)
        return super().formfield(**{'widget': widget})
