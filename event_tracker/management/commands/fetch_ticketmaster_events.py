import os
import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from events.models import Event, Location  # Adjust imports based on model structure

class Command(BaseCommand):
    help = "Fetch newly added events from Ticketmaster API"

    def handle(self, *args, **kwargs):
        base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
        api_key = os.getenv("TICKETMASTER_KEY")
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "countryCode": "GB",
            "startDateTime": seven_days_ago,
            "apikey": api_key
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json().get('_embedded', {}).get('events', [])
            for event_data in data:
                event_title = event_data.get('name')
                event_date = event_data.get('dates', {}).get('start', {}).get('localDate')
                venue_data = event_data.get('_embedded', {}).get('venues', [{}])[0]
                city = venue_data.get('city', {}).get('name', 'Unknown City')
                region = venue_data.get('name', 'Unknown Venue')

                location, _ = Location.objects.get_or_create(
                    city=city,
                    region=region,
                    country="GB"
                )

                if not Event.objects.filter(title=event_title, date=event_date, location=location).exists():
                    Event.objects.create(
                        title=event_title,
                        date=event_date,
                        location=location,
                        url=event_data.get('url'),
                        image=event_data.get('images', [{}])[0].get('url'),
                        description=event_data.get('info', 'No description available')
                    )
                    self.stdout.write(self.style.SUCCESS(f"Added event: {event_title} on {event_date}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to fetch events. Status: {response.status_code}"))
