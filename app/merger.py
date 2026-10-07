"""NAT and RADIUS data merger logic."""

from datetime import timedelta
from typing import Dict, List

from app.models import MergedRecord, NATRecord, RADIUSRecord


class NATradiusMerger:
    """Merge NAT and RADIUS records based on a time window and IP match."""

    DEFAULT_TIME_WINDOW = 5

    def __init__(self, time_window_minutes: int = DEFAULT_TIME_WINDOW):
        self.time_window = timedelta(minutes=time_window_minutes)

    def merge(self, nat_records: List[NATRecord], radius_records: List[RADIUSRecord]) -> List[MergedRecord]:
        """Return merged records matching NAT and RADIUS events."""
        merged: List[MergedRecord] = []
        radius_by_ip: Dict[str, List[RADIUSRecord]] = self._group_radius_by_ip(radius_records)

        for nat_record in nat_records:
            if nat_record.original_source_ip not in radius_by_ip:
                continue

            for radius_record in radius_by_ip[nat_record.original_source_ip]:
                if self._time_windows_overlap(nat_record.nat_time, radius_record.date_radius):
                    merged.append(
                        MergedRecord(
                            nat_time=nat_record.nat_time,
                            msisdn=radius_record.msisdn,
                            ip_private=radius_record.ip_private,
                            nat_type=nat_record.nat_type,
                            event_type=nat_record.event_type,
                            original_source_ip=nat_record.original_source_ip,
                            translated_ip=nat_record.translated_ip,
                            destination_ip=nat_record.destination_ip,
                            device_name=nat_record.device_name,
                            protocol=nat_record.protocol,
                            radius_state=radius_record.state,
                        )
                    )

        return merged

    def _group_radius_by_ip(self, radius_records: List[RADIUSRecord]) -> Dict[str, List[RADIUSRecord]]:
        grouped: Dict[str, List[RADIUSRecord]] = {}
        for record in radius_records:
            grouped.setdefault(record.ip_private, []).append(record)
        return grouped

    def _time_windows_overlap(self, nat_time, radius_time) -> bool:
        delta = abs((nat_time - radius_time).total_seconds())
        return delta <= self.time_window.total_seconds()
