from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL
    path('events/', views.fetch_events, name='events_list'),
]
