from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from events.models import Event

def new_events_view(request):
    # Define a 7-day window for "new" events
    seven_days_ago = timezone.now() - timedelta(days=7)

    # Get the search term from the query string
    search_term = request.GET.get('search', '').strip()

    # Base queryset for events created within the last 7 days in the UK
    events = Event.objects.filter(
        location__country="UK",  # Assuming location has a country attribute
        created_at__gte=seven_days_ago
    )

    # Apply search filtering if a search term is provided
    if search_term:
        events = events.filter(
            title__icontains=search_term
        ) | events.filter(
            location__city__icontains=search_term
        ) | events.filter(
            location__region__icontains=search_term
        )

    # Order by the most recently created events
    events = events.order_by('-created_at')

    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_tracker/new_events.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_term': search_term,
    })
