from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from events.models import Event

def new_events_view(request):
    # Set the "new events" window to events added in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Get search query parameters for filtering
    search_query = request.GET.get('q', '')  # For band name, show, etc.
    location_query = request.GET.get('location', '')  # For location filter
    
    # Filter for events added in the last 7 days based on `created_at`
    events = Event.objects.filter(
        created_at__gte=seven_days_ago,  # Events added in the last 7 days
        location__country="GB"           # Only events in the UK
    )
    
    # Apply search filters if provided
    if search_query:
        events = events.filter(title__icontains=search_query)
    if location_query:
        events = events.filter(location__city__icontains=location_query)
    
    # Order events by creation date (recently added first)
    events = events.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_tracker/new_events.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'location_query': location_query,
    })
