
from django.contrib import admin
from events import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='index'),
    path('', include('events.urls')),
    path('events/', views.fetch_events, name='events_list'),
    path('new-events/', include('event_tracker.urls')),
]
