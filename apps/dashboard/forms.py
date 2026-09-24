from django import forms

from apps.portfolio.models import Project


class DashboardModelForm(forms.ModelForm):
    """Common dashboard form styling and server-enforced publishing restriction."""

    class Meta:
        fields = ()

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if isinstance(self.instance, Project) and "status" in self.fields:
            if not user or not user.has_perm("portfolio.publish_project"):
                self.fields.pop("status")
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "checkbox-control"
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs["class"] = "select-control"
            else:
                field.widget.attrs["class"] = "input-control"
            if isinstance(field.widget, forms.DateInput):
                field.widget.input_type = "date"
