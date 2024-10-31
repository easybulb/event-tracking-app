from django.shortcuts import render
from events.models import Event  # Import from the correct app

def new_events_view(request):
    events = Event.objects.filter(
        location__city__in=["Manchester"],  # If your Location model has city field
        location__region__in=["Co-op Live", "O2 Manchester"]
    ).order_by('-date')
    return render(request, 'event_tracker/new_events.html', {'events': events})
