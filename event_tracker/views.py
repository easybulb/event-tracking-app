from django.shortcuts import render
from events.models import Event, Location


def new_events_view(request):
    # Filter events where the related location name is either "Co-op Live, Manchester" or "O2 Manchester"
    locations = Location.objects.filter(city="Manchester").filter(
        city__in=["Co-op Live", "O2"]
    )
    events = Event.objects.filter(location__in=locations).order_by('-date')
    return render(request, 'event_tracker/new_events.html', {'events': events})