import os
import requests
from django.shortcuts import render

def home(request):
    return render(request, 'events/index.html')


def fetch_events(request):
    city = "Manchester"
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?city=Manchester&apikey=WNA1iLdAjBEG1KhzGnXV4uYvlicJFbnD"
    response = requests.get(url)
    
    events = []
    if response.status_code == 200:
        raw_events = response.json().get('_embedded', {}).get('events', [])
        for event in raw_events:
            events.append({
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('localDate'),
                'time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0].get('name')
            })
    else:
        print(f"Error fetching events: {response.status_code} - {response.text}")

    return render(request, 'events_list.html', {'events': events})
