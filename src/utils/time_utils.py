"""
Timezone utilities for converting UTC times to Beijing time
"""

import pytz
from datetime import datetime
from typing import Union, Optional


def utc_to_beijing(utc_dt: Union[datetime, float, None]) -> datetime:
    """
    Convert UTC datetime to Beijing time (UTC+8)
    
    Args:
        utc_dt: UTC datetime object, timestamp, or None
        
    Returns:
        Beijing time datetime object
    """
    if utc_dt is None:
        return datetime.now(pytz.timezone('Asia/Shanghai'))
    
    # If it's a timestamp (float/int), convert to datetime first
    if isinstance(utc_dt, (int, float)):
        utc_dt = datetime.fromtimestamp(utc_dt, tz=pytz.UTC)
    elif isinstance(utc_dt, datetime) and utc_dt.tzinfo is None:
        # If datetime has no timezone info, assume it's naive UTC
        utc_dt = pytz.UTC.localize(utc_dt)
    
    # Convert to Beijing time
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_dt = utc_dt.astimezone(beijing_tz)
    
    return beijing_dt


def format_beijing_time(utc_dt: Union[datetime, float, None], format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format UTC datetime as Beijing time string
    
    Args:
        utc_dt: UTC datetime object, timestamp, or None
        format_str: Format string (default: '%Y-%m-%d %H:%M:%S')
        
    Returns:
        Formatted Beijing time string
    """
    beijing_time = utc_to_beijing(utc_dt)
    return beijing_time.strftime(format_str)


def now_beijing() -> datetime:
    """
    Get current time in Beijing timezone
    
    Returns:
        Current Beijing time datetime object
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)


def format_current_beijing(format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Get current Beijing time formatted as string
    
    Args:
        format_str: Format string (default: '%Y-%m-%d %H:%M:%S')
        
    Returns:
        Formatted current Beijing time string
    """
    return now_beijing().strftime(format_str)