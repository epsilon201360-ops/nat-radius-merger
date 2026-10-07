"""Utility functions for date parsing and formatting"""

from datetime import datetime
from typing import Optional


def normalize_date(date_str: str, file_type: str) -> datetime:
    """
    Normalize date string from NAT (Type A) or RADIUS (Type B) file
    
    Args:
        date_str: Date string to parse
        file_type: 'A' for NAT or 'B' for RADIUS
    
    Returns:
        datetime object
    """
    if not date_str or not date_str.strip():
        return datetime.now()
    
    date_str = date_str.strip()
    
    # NAT (Type A) format: typically "2026-10-06 11:42:20"
    if file_type == 'A':
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d/%m/%Y %H:%M:%S",
        ]
    # RADIUS (Type B) format: "2026-10-06 11:42:20.287748"
    else:
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # If all formats fail, return current time
    return datetime.now()


def format_date(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    return dt.strftime(format_str)


def seconds_to_duration(seconds: int) -> str:
    """Convert seconds to human readable duration"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)
