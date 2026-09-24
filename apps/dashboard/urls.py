from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/create/", views.ProfileCreateView.as_view(), name="profile-create"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("settings/create/", views.SettingsCreateView.as_view(), name="settings-create"),
    path("content/<slug:key>/", views.ContentListView.as_view(), name="content-list"),
    path("content/<slug:key>/new/", views.ContentCreateView.as_view(), name="content-create"),
    path("content/<slug:key>/<int:pk>/edit/", views.ContentUpdateView.as_view(), name="content-update"),
    path("content/<slug:key>/<int:pk>/delete/", views.ContentDeleteView.as_view(), name="content-delete"),
]
