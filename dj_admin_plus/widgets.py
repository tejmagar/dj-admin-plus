import json
from typing import Optional

from django.forms import Widget


class DJFileInput(Widget):
    template_name = 'dj_admin_plus/widgets/file-input.html'

    def __init__(self, attrs, image_preview: Optional[bool] = False):
        if attrs is not None:
            attrs = attrs.copy()

        self.image_preview = image_preview
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        if value:
            attrs['required'] = False

        context = super().get_context(name, value, attrs)

        context['widget']['image_preview'] = True if self.image_preview and value else False
        context['widget']['preview_url'] = value.url if value else None
        return context


class TinyMCE(Widget):
    template_name = 'dj_admin_plus/widgets/tinymce.html'

    class Media:
        js = ['tinymce/js/tinymce/tinymce.min.js']

    def __init__(self, attrs, tinymce_config=None):
        if attrs is not None:
            attrs = attrs.copy()

        self.tinymce_config = tinymce_config
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if not self.tinymce_config:
            self.tinymce_config = {}

        self.tinymce_config['branding'] = False
        self.tinymce_config['promotion'] = False
        self.tinymce_config['selector'] = f'#{name}'
        context['widget']['tinymce_config'] = json.dumps(self.tinymce_config)
        return context
