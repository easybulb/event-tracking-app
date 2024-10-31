# event_tracker/tasks.py
import os
import requests
from datetime import datetime
from celery import shared_task
from .models import Event  # Assume Event model stores relevant data

@shared_task
def poll_ticketmaster_api():
    venues = ["Co-op Live, Manchester", "O2 Manchester"]
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    api_key = os.getenv("TICKETMASTER_KEY")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    for venue in venues:
        params = {
            "keyword": venue,
            "countryCode": "GB",
            "startDateTime": current_time,
            "apikey": api_key
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json().get('_embedded', {}).get('events', [])
            
            for event_data in data:
                event_name = event_data.get('name')
                event_date = event_data.get('dates', {}).get('start', {}).get('localDate')
                
                # Check if the event is new
                if not Event.objects.filter(name=event_name, date=event_date).exists():
                    Event.objects.create(
                        name=event_name,
                        date=event_date,
                        venue=venue,
                        url=event_data.get('url'),
                        image=event_data.get('images', [{}])[0].get('url')
                    )
