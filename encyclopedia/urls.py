from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("random", views.random, name="random"),
    path("edit/<str:search>", views.edit, name="edit"),
    path("<str:search>", views.entry, name="entry")
]
