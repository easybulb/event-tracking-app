import os
import requests
from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'events/index.html')


def fetch_events(request):
    city = "Manchester"
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")  # Correct date format
    page = request.GET.get('page', 1)

    url = (
        f"https://app.ticketmaster.com/discovery/v2/events.json?"
        f"city={city}&startDateTime={current_time}&page={page}&apikey={os.getenv('TICKETMASTER_KEY')}"
    )
    response = requests.get(url)

    events = []
    next_page = None
    if response.status_code == 200:
        data = response.json().get('_embedded', {}).get('events', [])
        for event in data:
            events.append({
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('localDate'),
                'time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0].get('name')
            })
        # Pagination
        next_page = response.json().get('page', {}).get('number') + 1 if response.json().get('page', {}).get('totalPages', 1) > int(page) else None
    else:
        print(f"Error fetching events: {response.status_code} - {response.text}")

    return render(request, 'events_list.html', {'events': events, 'next_page': next_page})