import os
import requests
from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'events/index.html')

def fetch_events(request):
    city = request.GET.get('city', 'Manchester')
    venue = request.GET.get('venue', '')
    sorting = request.GET.get('sorting', 'popularity')
    page = request.GET.get('page', 1)
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    sort_param = "relevance,desc" if sorting == "popularity" else "date,asc"

    # Add venue to the query if provided
    url = (
        f"https://app.ticketmaster.com/discovery/v2/events.json?"
        f"city={city}&countryCode=GB&startDateTime={current_time}&page={page}&sort={sort_param}"
        f"&apikey={os.getenv('TICKETMASTER_KEY')}"
    )
    if venue:
        url += f"&keyword={venue}"

    response = requests.get(url)

    events = []
    next_page = None
    if response.status_code == 200:
        data = response.json().get('_embedded', {}).get('events', [])
        for event in data:
            # Adjusted price retrieval
            price_info = event.get('priceRanges', [{}])[0]
            min_price = price_info.get('min')
            max_price = price_info.get('max')
            
            # Format price based on availability
            price = None
            if min_price and max_price:
                price = f"£{min_price} - £{max_price}"
            elif min_price:
                price = f"£{min_price}"

            events.append({
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('localDate'),
                'time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0].get('name'),
                'price': price,  # Updated price formatting
                'image': event.get('images', [{}])[0].get('url'),
                'url': event.get('url')
            })
        next_page = response.json().get('page', {}).get('number') + 1 if response.json().get('page', {}).get('totalPages', 1) > int(page) else None
    else:
        print(f"Error fetching events: {response.status_code} - {response.text}")

    return render(request, 'events_list.html', {
        'events': events,
        'next_page': next_page,
        'city': city,
        'venue': venue,
        'sorting': sorting
    })
