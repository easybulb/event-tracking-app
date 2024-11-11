from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from events.models import Event

def new_events_view(request):
    # Set the "new events" window to 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Get search term from query parameters
    search_term = request.GET.get('search', '').strip()
    
    # Base queryset for events added in the last 7 days in the UK
    events = Event.objects.filter(
        location__country="UK",
        created_at__gte=seven_days_ago  # Only events added in the last 7 days
    )
    
    # Filter by search term if provided
    if search_term:
        events = events.filter(
            title__icontains=search_term
        ) | events.filter(
            location__city__icontains=search_term
        ) | events.filter(
            location__region__icontains=search_term
        )

    # Order by the most recently added events
    events = events.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_tracker/new_events.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_term': search_term,  # Pass the search term back to the template
    })
