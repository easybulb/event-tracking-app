import os
import requests
import random
from django.shortcuts import render, redirect
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.utils.dateparse import parse_date
from .models import ContactMessage
from .forms import ContactForm

def home(request):
    # Fetching events from the API
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = (
        f"https://app.ticketmaster.com/discovery/v2/events.json?"
        f"countryCode=GB&startDateTime={current_time}&size=10"
        f"&apikey={os.getenv('TICKETMASTER_KEY')}"
    )

    response = requests.get(url)
    featured_events = []

    if response.status_code == 200:
        data = response.json().get('_embedded', {}).get('events', [])
        unique_events = random.sample(data, min(len(data), 3))
        
        for event in unique_events:
            price_info = event.get('priceRanges', [{}])[0]
            min_price = price_info.get('min')
            max_price = price_info.get('max')
            price = f"£{min_price} - £{max_price}" if min_price and max_price else f"£{min_price}" if min_price else None

            featured_events.append({
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('localDate'),
                'time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0].get('name'),
                'price': price,
                'image': event.get('images', [{}])[0].get('url'),
                'url': event.get('url')
            })

    return render(request, 'events/index.html', {'featured_events': featured_events})


def fetch_events(request):
    anything_query = request.GET.get('anything', '').strip()
    date_filter = request.GET.get('date', '').strip()
    page = int(request.GET.get('page', 1))

    # Base URL for Ticketmaster API
    base_url = f"https://app.ticketmaster.com/discovery/v2/events.json?countryCode=GB&page={page}&apikey={os.getenv('TICKETMASTER_KEY')}"

    # Construct URL based on the provided search input
    if anything_query:
        url = f"{base_url}&keyword={anything_query}"
    elif date_filter:
        parsed_date = parse_date(date_filter)
        if parsed_date:
            start_date_time = f"{parsed_date}T00:00:00Z"
            end_date_time = f"{parsed_date}T23:59:59Z"
            url = f"{base_url}&startDateTime={start_date_time}&endDateTime={end_date_time}"
        else:
            url = base_url
    else:
        url = base_url

    response = requests.get(url)

    events = []
    next_page = None
    previous_page = None
    total_pages = 1  # Default to 1 if pagination is not available
    if response.status_code == 200:
        data = response.json().get('_embedded', {}).get('events', [])
        for event in data:
            price_info = event.get('priceRanges', [{}])[0]
            min_price = price_info.get('min')
            max_price = price_info.get('max')
            price = f"£{min_price} - £{max_price}" if min_price and max_price else f"£{min_price}" if min_price else None

            # Get location details, including full address if available
            venue_data = event.get('_embedded', {}).get('venues', [{}])[0]
            venue_name = venue_data.get('name')
            city = venue_data.get('city', {}).get('name', '')
            state = venue_data.get('state', {}).get('name', '')
            country = venue_data.get('country', {}).get('name', '')
            address = f"{venue_name}, {city}, {state}, {country}".strip(", ")

            events.append({
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('localDate'),
                'time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': venue_name,
                'location': address,
                'price': price,
                'image': event.get('images', [{}])[0].get('url'),
                'url': event.get('url')
            })
        
        pagination_info = response.json().get('page', {})
        total_pages = pagination_info.get('totalPages', 1)
        if page < total_pages:
            next_page = page + 1
        if page > 1:
            previous_page = page - 1

    # Generate the list of page numbers
    page_numbers = list(range(1, total_pages + 1))

    return render(request, 'events/events_list.html', {
        'events': events,
        'next_page': next_page,
        'previous_page': previous_page,
        'current_page': page,
        'page_numbers': page_numbers,
        'anything_query': anything_query,
        'date_filter': date_filter
    })
    
def about(request):
    return render(request, 'events/about.html')

def contact(request):
    return render(request, 'events/contact.html')

def send_message(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
            )
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ContactForm()

    return render(request, 'events/contact.html', {'form': form})