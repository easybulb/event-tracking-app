import os
import requests
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from .models import ContactMessage
from .forms import ContactForm

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
                'price': price,
                'image': event.get('images', [{}])[0].get('url'),
                'url': event.get('url')
            })
        next_page = response.json().get('page', {}).get('number') + 1 if response.json().get('page', {}).get('totalPages', 1) > int(page) else None
    else:
        print(f"Error fetching events: {response.status_code} - {response.text}")

    return render(request, 'events/events_list.html', {
        'events': events,
        'next_page': next_page,
        'city': city,
        'venue': venue,
        'sorting': sorting
    })

def about(request):
    return render(request, 'events/about.html')

def contact(request):
    return render(request, 'events/contact.html')

def send_message(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to the database
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

