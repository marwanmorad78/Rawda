import inspect

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden

from apps.core.localization import get_language
from apps.dashboard.localization import get_dashboard_strings


class DashboardLocalizationMixin:
    def get_language(self):
        return get_language(self.request)

    def get_dashboard_ui(self):
        return get_dashboard_strings(self.get_language())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("dashboard_ui", self.get_dashboard_ui())
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_class = self.get_form_class()
        try:
            signature = inspect.signature(form_class.__init__)
        except (TypeError, ValueError):
            signature = None

        if signature and "language" in signature.parameters:
            kwargs["language"] = self.get_language()
        return kwargs


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            language = get_language(self.request)
            return HttpResponseForbidden(get_dashboard_strings(language)["permission_denied"])
        return super().handle_no_permission()
