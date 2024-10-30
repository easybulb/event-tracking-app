from django.shortcuts import render
import requests

def home(request):
    return render(request, 'events/index.html')

def fetch_events(request):
    city = "Manchester"  # Example city; you could make this dynamic later
    url = f"https://www.eventbriteapi.com/v3/events/search/?location.address={city}&location.within=50km"
    headers = {"Authorization": f"Bearer MZCASTP7MNUMGV2QOF5C"}
    response = requests.get(url, headers=headers)
    events = response.json().get('events', [])
    return render(request, 'events_list.html', {'events': events})

