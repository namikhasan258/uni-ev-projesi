"""
Timezone utilities for Turkish time (UTC+3)
"""
from datetime import datetime, timedelta
import pytz

# Turkish timezone
TURKISH_TZ = pytz.timezone('Europe/Istanbul')

def get_turkish_time():
    """Get current time in Turkish timezone"""
    return datetime.now(TURKISH_TZ)

def utc_to_turkish(utc_time):
    """Convert UTC datetime to Turkish time"""
    if utc_time is None:
        return None
    
    # If naive datetime, assume it's UTC
    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)
    
    # Convert to Turkish time
    return utc_time.astimezone(TURKISH_TZ)

def format_turkish_time(dt):
    """Format datetime in Turkish format"""
    if dt is None:
        return None
    
    turkish_dt = utc_to_turkish(dt)
    return turkish_dt.strftime('%d.%m.%Y %H:%M')

def to_iso_turkish(dt):
    """Convert to ISO format in Turkish time"""
    if dt is None:
        return None
    
    turkish_dt = utc_to_turkish(dt)
    return turkish_dt.isoformat()
