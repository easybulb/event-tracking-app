from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from events.models import Event

def new_events_view(request):
    # Set window for "new events" to 7 days (using `created_at` in DB)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Retrieve and filter only events added to the database in the last 7 days
    events = Event.objects.filter(
        created_at__gte=seven_days_ago,  # Newly added to the database in the past 7 days
        location__country="GB"           # Limit to UK events
    ).order_by('-created_at')
    
    # Search filters
    search_query = request.GET.get('q', '')
    location_query = request.GET.get('location', '')
    
    if search_query:
        events = events.filter(title__icontains=search_query)
    if location_query:
        events = events.filter(location__city__icontains=location_query)
    
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
