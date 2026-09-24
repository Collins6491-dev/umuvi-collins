from django.urls import path

from .views import submit_contact


app_name = "contact"

urlpatterns = [path("submit/", submit_contact, name="submit")]
