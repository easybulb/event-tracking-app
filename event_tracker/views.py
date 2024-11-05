from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from events.models import Event

def new_events_view(request):
    # Set the "new events" window to 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    events = Event.objects.filter(
        location__city__in=["Manchester"],
        location__region__in=["Co-op Live", "O2 Manchester"],
        created_at__gte=seven_days_ago  # Only events added in the last 7 days
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(events, 12)  # Show 10 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_tracker/new_events.html', {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })
