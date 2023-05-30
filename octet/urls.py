from django.urls import path

from app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("event/<int:event_id>", views.event, name="event"),
    path("contest/<int:contest_id>", views.contest, name="contest"),
]
