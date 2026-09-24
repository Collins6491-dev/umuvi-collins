from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class DashboardAccessMixin(AccessMixin):
    """Dashboard access requires both authentication and explicit staff membership."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied("Dashboard access is restricted.")
        return super().dispatch(request, *args, **kwargs)


class DashboardPermissionMixin(DashboardAccessMixin):
    permission_required = ""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied("Dashboard access is restricted.")
        if self.permission_required and not request.user.has_perm(self.permission_required):
            raise PermissionDenied("You do not have permission to perform this action.")
        return super(DashboardAccessMixin, self).dispatch(request, *args, **kwargs)
