from django import forms

from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    # A honeypot is intentionally not a model field; bots that fill it are silently rejected.
    company_website = forms.CharField(required=False, label="Website", widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def clean_company_website(self):
        value = self.cleaned_data["company_website"]
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value
