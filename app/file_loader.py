import gzip
import csv
from pathlib import Path
from typing import List, Tuple
from app.models import NATRecord, RADIUSRecord, FileMetadata
from app.utils import normalize_date

class FileLoader:
    """Handles loading and parsing of NAT and RADIUS files"""
    
    @staticmethod
    def load_nat_file(file_path: str, max_lines: int = 100) -> Tuple[List[NATRecord], FileMetadata]:
        """
        Load NAT (Type A) file from .gz
        
        Args:
            file_path: Path to .gz file
            max_lines: Maximum lines to load into memory for display
        
        Returns:
            Tuple of (records_list, metadata)
        """
        records = []
        total_lines = 0
        
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader):
                    total_lines += 1
                    
                    if idx < max_lines:
                        try:
                            nat_time = normalize_date(row.get('NAT Time', ''), 'A')
                            record = NATRecord(
                                nat_time=nat_time,
                                device_name=row.get('Device Name', '').strip(),
                                nat_type=row.get('NAT Type', '').strip(),
                                event_type=row.get('Event Type', '').strip(),
                                original_source_ip=row.get('Original Source IP', '').strip(),
                                original_source_port=row.get('Original Source Port', '').strip(),
                                translated_ip=row.get('Translated IP', '').strip(),
                                translated_port=row.get('Translated Port', '').strip() or '-',
                                destination_ip=row.get('Destination IP', '').strip(),
                                destination_port=row.get('Destination Port', '').strip(),
                                protocol=row.get('Protocol', '').strip()
                            )
                            records.append(record)
                        except Exception as e:
                            print(f"Error parsing NAT record at line {idx}: {e}")
                            continue
            
            metadata = FileMetadata(
                filename=Path(file_path).name,
                file_type='A',
                lines_loaded=len(records),
                lines_total=total_lines,
                file_path=file_path
            )
            
            return records, metadata
        
        except Exception as e:
            print(f"Error loading NAT file: {e}")
            return [], None
    
    @staticmethod
    def load_radius_file(file_path: str, max_lines: int = 100) -> Tuple[List[RADIUSRecord], FileMetadata]:
        """
        Load RADIUS (Type B) file from text with | delimiter
        
        Args:
            file_path: Path to text file
            max_lines: Maximum lines to load into memory for display
        
        Returns:
            Tuple of (records_list, metadata)
        """
        records = []
        total_lines = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    total_lines += 1
                    
                    if idx < max_lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            parts = line.split('|')
                            if len(parts) < 4:
                                print(f"Invalid RADIUS record at line {idx}: not enough fields")
                                continue
                            
                            date_radius = normalize_date(parts[0].strip(), 'B')
                            state = int(parts[1].strip())
                            msisdn = parts[2].strip()
                            ip_private = parts[3].strip()
                            
                            record = RADIUSRecord(
                                date_radius=date_radius,
                                state=state,
                                msisdn=msisdn,
                                ip_private=ip_private
                            )
                            records.append(record)
                        except Exception as e:
                            print(f"Error parsing RADIUS record at line {idx}: {e}")
                            continue
            
            metadata = FileMetadata(
                filename=Path(file_path).name,
                file_type='B',
                lines_loaded=len(records),
                lines_total=total_lines,
                file_path=file_path
            )
            
            return records, metadata
        
        except Exception as e:
            print(f"Error loading RADIUS file: {e}")
            return [], None
    
    @staticmethod
    def load_all_nat_records(file_paths: List[str]) -> List[NATRecord]:
        """Load all records from multiple NAT files without limit"""
        all_records = []
        
        for file_path in file_paths:
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        try:
                            nat_time = normalize_date(row.get('NAT Time', ''), 'A')
                            record = NATRecord(
                                nat_time=nat_time,
                                device_name=row.get('Device Name', '').strip(),
                                nat_type=row.get('NAT Type', '').strip(),
                                event_type=row.get('Event Type', '').strip(),
                                original_source_ip=row.get('Original Source IP', '').strip(),
                                original_source_port=row.get('Original Source Port', '').strip(),
                                translated_ip=row.get('Translated IP', '').strip(),
                                translated_port=row.get('Translated Port', '').strip() or '-',
                                destination_ip=row.get('Destination IP', '').strip(),
                                destination_port=row.get('Destination Port', '').strip(),
                                protocol=row.get('Protocol', '').strip()
                            )
                            all_records.append(record)
                        except Exception as e:
                            continue
            except Exception as e:
                print(f"Error loading NAT file {file_path}: {e}")
                continue
        
        return all_records
    
    @staticmethod
    def load_all_radius_records(file_paths: List[str]) -> List[RADIUSRecord]:
        """Load all records from multiple RADIUS files without limit"""
        all_records = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            parts = line.split('|')
                            if len(parts) < 4:
                                continue
                            
                            date_radius = normalize_date(parts[0].strip(), 'B')
                            state = int(parts[1].strip())
                            msisdn = parts[2].strip()
                            ip_private = parts[3].strip()
                            
                            record = RADIUSRecord(
                                date_radius=date_radius,
                                state=state,
                                msisdn=msisdn,
                                ip_private=ip_private
                            )
                            all_records.append(record)
                        except Exception as e:
                            continue
            except Exception as e:
                print(f"Error loading RADIUS file {file_path}: {e}")
                continue
        
        return all_records
