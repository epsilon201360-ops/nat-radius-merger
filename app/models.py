"""Data models for NAT and RADIUS records."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NATRecord:
    """Model for NAT (Type A) record."""
    nat_time: datetime
    device_name: str
    nat_type: str
    event_type: str
    original_source_ip: str
    original_source_port: str
    translated_ip: str
    translated_port: str
    destination_ip: str
    destination_port: str
    protocol: str


@dataclass
class RADIUSRecord:
    """Model for RADIUS (Type B) record."""
    date_radius: datetime
    state: int
    msisdn: str
    ip_private: str


@dataclass
class FileMetadata:
    """Metadata about the loaded file."""
    filename: str
    file_type: str
    lines_loaded: int
    lines_total: int
    file_path: str


@dataclass
class MergedRecord:
    """Model for merged NAT/RADIUS record."""
    nat_time: datetime
    msisdn: str
    ip_private: str
    nat_type: str
    event_type: str
    original_source_ip: str
    translated_ip: str
    destination_ip: str
    device_name: str
    protocol: str
    radius_state: int
    connection_duration: Optional[str] = None
