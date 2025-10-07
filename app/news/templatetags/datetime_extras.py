from django import template
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import datetime

register = template.Library()

@register.filter
def smart_datetime(value):
    """
    Display datetime in a smart way:
    - If published_at exists: show "2 hours ago" for recent, or "6 Oct 2025" for older
    - If only created_at: show "Added 2 hours ago"
    """
    if not value:
        return ""
    
    now = timezone.now()
    diff = now - value
    
    # If less than 24 hours, show relative time
    if diff.days == 0:
        return f"{timesince(value, now)} ago"
    
    # If less than 7 days, show "X days ago"
    elif diff.days < 7:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    
    # For older dates, show formatted date
    else:
        return value.strftime("%-d %b %Y")

@register.filter
def publication_time(article):
    """
    Show publication time if available, otherwise show when it was added to our database
    """
    if article.published_at:
        return smart_datetime(article.published_at)
    else:
        # Fallback to created_at with indication it's when we added it
        return f"Added {smart_datetime(article.created_at)}"