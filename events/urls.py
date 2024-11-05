from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL
    path('events/', views.fetch_events, name='events_list'),
    path('events/', views.fetch_events, name='fetch_events'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('send_message/', views.send_message, name='send_message'),
]
