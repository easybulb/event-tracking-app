import os
import requests
import logging
from datetime import datetime
from celery import shared_task
from events.models import Event, Location

# Configure logging
logger = logging.getLogger(__name__)

@shared_task
def poll_ticketmaster_api():
    logger.info("Starting poll_ticketmaster_api task.")
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    api_key = os.getenv("TICKETMASTER_KEY")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Query for events across the UK
    params = {
        "countryCode": "GB",
        "startDateTime": current_time,
        "apikey": api_key
    }

    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json().get('_embedded', {}).get('events', [])
            
            # Log the number of events fetched
            logger.info(f"Fetched {len(data)} events from Ticketmaster.")
            
            for event_data in data:
                event_title = event_data.get('name')
                event_date = event_data.get('dates', {}).get('start', {}).get('localDate')
                event_time = event_data.get('dates', {}).get('start', {}).get('localTime')
                event_url = event_data.get('url')
                event_image = event_data.get('images', [{}])[0].get('url')
                
                venue_data = event_data.get('_embedded', {}).get('venues', [{}])[0]
                city = venue_data.get('city', {}).get('name', 'Unknown City')
                region = venue_data.get('name', 'Unknown Venue')
                country = "GB"

                # Ensure the location exists or create it
                location, created = Location.objects.get_or_create(
                    city=city,
                    region=region,
                    country=country
                )
                
                if created:
                    logger.info(f"Created new location: {city}, {region}")

                # Only add the event if it doesn’t already exist
                if not Event.objects.filter(title=event_title, date=event_date, location=location).exists():
                    event = Event.objects.create(
                        title=event_title,
                        description=event_data.get('info', 'No description available'),
                        date=event_date,
                        time=event_time,
                        location=location,
                        url=event_url,
                        image=event_image
                    )
                    logger.info(f"Created new event: {event.title} on {event.date}")
                else:
                    logger.info(f"Event already exists: {event_title} on {event_date}")
        else:
            logger.error(f"Failed to fetch events. Status code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logger.error(f"An error occurred in poll_ticketmaster_api: {e}")
        raise  # re-raise the exception for visibility
