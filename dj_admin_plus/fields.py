from django.db import models

from .widgets import TinyMCE


class HTMLField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.attrs = kwargs.get('attrs')
        self.tinymce_config = kwargs.get('tinymce_config')

        if self.attrs:
            self.attrs = self.attrs.copy()
            kwargs.pop('attrs')

        if self.tinymce_config:
            self.tinymce_config = self.tinymce_config.copy()
            kwargs.pop('tinymce_config')

        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        widget_attrs = self.attrs

        if not self.attrs:
            widget_attrs = {'rows': 4, 'cols': 40}

        widget = TinyMCE(attrs=widget_attrs, tinymce_config=self.tinymce_config)
        return super().formfield(**{'widget': widget})
