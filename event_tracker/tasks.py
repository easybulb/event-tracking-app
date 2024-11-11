import os
import requests
from datetime import datetime
from celery import shared_task
from events.models import Event, Location

@shared_task
def poll_ticketmaster_api():
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    api_key = os.getenv("TICKETMASTER_KEY")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Fetch all events in the UK
    params = {
        "countryCode": "GB",
        "startDateTime": current_time,
        "apikey": api_key,
        "size": 200  # Fetch a larger batch of events if available
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json().get('_embedded', {}).get('events', [])
        
        for event_data in data:
            event_title = event_data.get('name')
            event_date = event_data.get('dates', {}).get('start', {}).get('localDate')
            event_time = event_data.get('dates', {}).get('start', {}).get('localTime')
            event_url = event_data.get('url')
            event_image = event_data.get('images', [{}])[0].get('url')
            
            # Extract location details
            venue_info = event_data.get('_embedded', {}).get('venues', [{}])[0]
            city = venue_info.get('city', {}).get('name', 'Unknown')
            region = venue_info.get('name', 'Unknown')
            country = venue_info.get('country', {}).get('name', 'Unknown')

            # Ensure the location exists or create it
            location, created = Location.objects.get_or_create(
                city=city,
                region=region,
                country=country
            )
            
            # Only add the event if it doesn’t already exist
            if not Event.objects.filter(title=event_title, date=event_date, location=location).exists():
                Event.objects.create(
                    title=event_title,
                    description=event_data.get('info', 'No description available'),
                    date=event_date,
                    time=event_time,
                    location=location,
                    url=event_url,
                    image=event_image
                )
