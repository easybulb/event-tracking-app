from django.db import models

# Category model defines event types like music, sports, theater.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Location model represents city, region, and country.
class Location(models.Model):
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.region}, {self.country}" if self.region else f"{self.city}, {self.country}"

# Event model represents individual events, linked to a category and location.
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields for URL and image
    url = models.URLField(max_length=500, blank=True, null=True)
    image = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title


# models.py
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

