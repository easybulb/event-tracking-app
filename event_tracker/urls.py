# event_tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.new_events_view, name='new_events'),
]
