from typing import Optional

from django.forms import Widget


class DJFileInput(Widget):
    template_name = "dj_admin_plus/widgets/file-input.html"

    def __init__(self, attrs, image_preview: Optional[bool] = False):
        if attrs is not None:
            attrs = attrs.copy()

        self.image_preview = image_preview
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['image_preview'] = True if self.image_preview and value else False
        context['widget']['preview_url'] = value.url if value else None
        return context
