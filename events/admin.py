from django.contrib import admin
from .models import Event, Location, Category, ContactMessage

# Register your models here.

admin.site.register(Event)
admin.site.register(Location)
admin.site.register(Category)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)


