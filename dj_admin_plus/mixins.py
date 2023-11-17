from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse


class AdminLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    redirect_url = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{reverse("dj_admin_plus_login")}?next={request.path}')

        return super().dispatch(request, *args, **kwargs)
