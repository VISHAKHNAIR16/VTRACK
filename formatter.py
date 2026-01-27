"""
Card formatting functions
"""
import re
from typing import Dict, Any
from utils import clean_name, clean_phone_number, clean_flight_number, format_date, format_pax_count, clean_time
import pandas as pd


def get_pickup_time_for_sorting(record: Dict[str, Any]) -> str:
    """Extract pickup time for sorting purposes."""
    if record['type'] == 'individual':
        # For individual cards
        pickup_time = record['data'].get('PickupTime', '')
        if pd.isna(pickup_time) or not pickup_time:
            return "99:99"  # Put at the end if no time
        # Convert to proper HH:MM format
        time_str = str(pickup_time).strip()
        if ':' in time_str:
            parts = time_str.split(':')
            hours = parts[0].zfill(2)
            minutes = parts[1][:2].zfill(2) if len(parts) > 1 else "00"
            return f"{hours}:{minutes}"
        elif len(time_str) == 4 and time_str.isdigit():
            return f"{time_str[:2]}:{time_str[2:]}"
        else:
            return "99:99"
    else:
        # For shared groups, use the first passenger's pickup time
        if record['passengers']:
            pickup_time = record['passengers'][0].get('pickup_time', '')
            if pickup_time:
                return pickup_time
        # Fallback to common pickup time
        return record['common_data'].get('pickup_time', '99:99')


def create_shared_card_text(group_data: Dict[str, Any]) -> str:
    """
    Create formatted text for shared tours with COMPLETE info for EACH passenger.
    """
    passengers = group_data['passengers']
    common = group_data['common_data']
    
    lines = []
    
    # For each passenger in the group
    for i, passenger in enumerate(passengers):
        # Get individual passenger's row data
        row_data = passenger.get('row_data', {})  # We need to store this in grouping
        
        # Passenger header (TBZ PNR LegId)
        lines.append(f"TBZ {passenger['pnr']} {passenger['leg_id']}")
        
        # Date (only for first passenger to avoid repetition)
        if i == 0 and common['service_date']:
            lines.append(common['service_date'])
        elif i > 0 and common['service_date']:
            # For subsequent passengers, we can skip the date or leave blank
            pass
        
        # Guest name with PAX count
        adult = passenger['adult']
        child = passenger['child']
        infant = passenger['infant']
        
        # Format PAX exactly as per requirements
        if child > 0 or infant > 0:
            if child > 0 and infant > 0:
                pax_str = f"{adult}+{child}+{infant} PAX"
            elif child > 0:
                pax_str = f"{adult}+{child} PAX"
            elif infant > 0:
                pax_str = f"{adult}+{infant} PAX"
        else:
            pax_str = f"{adult} PAX"
        
        lines.append(f"{passenger['guest_name']} -- {pax_str}")
        
        # Phone numbers
        phones = []
        if passenger['whatsapp_no']:
            phones.append(passenger['whatsapp_no'])
        if passenger['alternate_no'] and passenger['alternate_no'] not in ['+91 1111111111', '+91 999999999', '']:
            phones.append(passenger['alternate_no'])
        
        for phone in phones:
            lines.append(phone)
        
        # FROM location (each passenger may have different pickup)
        if passenger['transfer_from']:
            lines.append(f"FROM : {passenger['transfer_from']}")
        
        # TO location - CRITICAL CHANGE: Get individual TO location
        # Try TransferTo first, then fall back to service_name
        transfer_to = passenger.get('transfer_to', '')
        if not transfer_to and row_data:
            transfer_to = str(row_data.get('TransferTo', '')).strip()
        if not transfer_to:
            # Fall back to service name
            transfer_to = common.get('service_name', '')
        
        if transfer_to:
            lines.append(f"TO   : {transfer_to}")
        
        # Service Name - CRITICAL: Show for EACH passenger
        service_name = passenger.get('service_name', '')
        if not service_name and row_data:
            service_name = str(row_data.get('ServiceName', '')).strip()
        if not service_name:
            service_name = common.get('service_name', '')
        
        if service_name:
            # Clean service text - REMOVE XRQT HERE
            service_name = re.sub(r'\s*XRQT\s*', ' ', service_name, flags=re.IGNORECASE)
            service_name = re.sub(r'<[^>]+>', '', service_name)
            service_name = ' '.join(service_name.split())
            lines.append(f"Service Name : {service_name}")
        
        # Pickup Time - CRITICAL: Show for EACH passenger if available
        pickup_time = passenger.get('pickup_time', '')
        if not pickup_time and row_data:
            pickup_time_raw = row_data.get('PickupTime', '')
            if pd.notna(pickup_time_raw):
                pickup_time = str(pickup_time_raw).strip()
                # Format time properly
                if ':' in pickup_time:
                    parts = pickup_time.split(':')
                    if len(parts) >= 2:
                        hours = parts[0].zfill(2)
                        minutes = parts[1][:2].zfill(2)
                        pickup_time = f"{hours}:{minutes}"
        
        if pickup_time and pickup_time not in ['', '00:00', '0:00']:
            lines.append(f"PICK UP TIME {pickup_time}")
        elif common['pickup_time'] and i == 0:  # Fallback for first passenger
            lines.append(f"PICK UP TIME {common['pickup_time']}")
        
        # Flight Number - CRITICAL: Show for EACH passenger if available
        flight_no = ''
        if row_data:
            flight_no_raw = row_data.get('FlightNo', '')
            if pd.notna(flight_no_raw):
                flight_no = clean_flight_number(str(flight_no_raw))
        
        if flight_no:
            lines.append(f"FLIGHT NUMBER : {flight_no}")
        
        # Add empty line between passengers (except after last one)
        if i < len(passengers) - 1:
            lines.append("")
    
    # Add empty line before service type
    lines.append("")
    
    # Service Type
    if common['service_type']:
        lines.append(common['service_type'])
    
    # Driver and vehicle info (ONLY ONCE at the end)
    # Only add these lines if we have at least SOME info
    # Vehicle name first
    if common['vehicle_name'] and common['vehicle_name'].strip() not in ['', '-', 'N/A']:
        lines.append(common['vehicle_name'])
    elif common['driver_name'] or common['driver_number'] or common['vehicle_number']:
        # If we don't have vehicle name but have other info, add empty line for consistency
        lines.append("")
    
    # Driver name
    if common['driver_name'] and common['driver_name'].strip() not in ['', '-', 'N/A']:
        lines.append(common['driver_name'])
    
    # Driver number
    if common['driver_number'] and common['driver_number'].strip() not in ['', '-', 'N/A']:
        lines.append(common['driver_number'])
    
    # Vehicle number
    if common['vehicle_number'] and common['vehicle_number'].strip() not in ['', '-', 'N/A']:
        lines.append(common['vehicle_number'])
    
    # Add divider
    lines.append("")
    lines.append("=" * 48)
    
    return "\n".join(lines)


def create_card_text(row: Dict[str, Any]) -> str:
    """Create formatted text for a single card in EXACT format as per requirements."""
    import pandas as pd
    
    # Extract with safe defaults
    pnr = str(row.get('PNR', '')).strip()
    leg_id = str(row.get('LegId', '')).strip()
    guest_name = clean_name(row.get('GuestName', ''))
    whatsapp_no = clean_phone_number(row.get('WhatsappNo', ''))
    alternate_no = clean_phone_number(row.get('AlternateNumber', ''))
    
    # Get service name - try TourOptionName first, then ServiceName
    service_name = str(row.get('ServiceName', '')).strip()
    
    # REMOVE XRQT from service name for display
    service_name = re.sub(r'\s*XRQT\s*', ' ', service_name, flags=re.IGNORECASE)
    service_name = re.sub(r'\s+', ' ', service_name)  # Clean extra spaces
    
    service_text = service_name
    
    transfer_from = str(row.get('TransferFrom', '')).strip()
    transfer_to = str(row.get('TransferTo', '')).strip()
    if not transfer_to:
        transfer_to = service_text   # fallback to ServiceName / TourOptionName

    
    adult = int(row.get('Adult', 0)) if pd.notna(row.get('Adult')) else 0
    child = int(row.get('Child', 0)) if pd.notna(row.get('Child')) else 0
    infant = int(row.get('Infant', 0)) if pd.notna(row.get('Infant')) else 0
    
    service_date = format_date(row.get('ServiceDate', ''))
    service_type = str(row.get('ServiceType', '')).strip()
    
    pickup_time_raw = row.get('PickupTime', '')
    if pd.isna(pickup_time_raw):
        pickup_time = ""
    else:
        pickup_time = str(pickup_time_raw).strip()
        # Handle Excel time format and remove seconds
        if ':' not in pickup_time and len(pickup_time) == 4 and pickup_time.isdigit():
            pickup_time = f"{pickup_time[:2]}:{pickup_time[2:]}"
        elif ':' in pickup_time:
            # Ensure proper HH:MM format (no seconds)
            parts = pickup_time.split(':')
            if len(parts) >= 2:
                hours = parts[0].zfill(2)
                minutes = parts[1][:2].zfill(2)  # Only take first 2 digits
                pickup_time = f"{hours}:{minutes}"
    
    flight_no = clean_flight_number(row['FlightNo']) if 'FlightNo' in row else ""
    vehicle_name = str(row.get('VehicalName', '')).strip()
    driver_name = str(row.get('Driver Name', '')).strip()
    driver_number = str(row.get('Driver Number', '')).strip()
    vehicle_number = str(row.get('Vehicle Number', '')).strip()
    
    # Format passenger count
    pax_count = format_pax_count(adult, child, infant)
    
    # Format phone numbers - EXACT format as per requirements
    phones = []
    if whatsapp_no:
        phones.append(whatsapp_no)
    if alternate_no and alternate_no not in ['+91 1111111111', '+91 999999999', '+91 21', '']:
        phones.append(alternate_no)

    
    # Clean service text - remove HTML tags
    if service_text:
        service_text = re.sub(r'<br\s*/?>', ' ', service_text, flags=re.IGNORECASE)
        service_text = re.sub(r'<[^>]+>', '', service_text)
        service_text = ' '.join(service_text.split())
    
    # Build the formatted text EXACTLY as per requirements with proper line breaks
    lines = []
    
    # Line 1: TBZ PNR LegId (EXACT format with double space at end like in example)
    lines.append(f"TBZ {pnr} {leg_id}")
    
    
    # Line 3: Date
    if service_date:
        lines.append(service_date)
    
    # Line 4: Guest Name with PAX count (EXACT format - no space before PAX)
    if guest_name:
        lines.append(f"{guest_name} -- {pax_count}")
    
    # Line 5: Phone numbers with slash separator (EXACT spacing from example)
    for ph in phones:
        lines.append(ph)

    
    # Line 6: FROM (EXACT spacing with colon and space)
    if transfer_from:
        lines.append(f"FROM : {transfer_from}")
    
    # Line 7: TO (EXACT spacing with 3 spaces before colon like in example)
    if transfer_to:
        lines.append(f"TO   : {transfer_to}")
    
    # Line 8: Service description
    if service_text:
        lines.append(f"Service Name : {service_text}")
    
    # Line 9: Pickup Time (only if not 00:00)
    if pickup_time and pickup_time not in ['', '00:00', '0:00']:
        lines.append(f"PICK UP TIME {pickup_time}")
    
    # Line 10: Flight Number (if exists)
    if flight_no:
        lines.append(f"FLIGHT NUMBER : {flight_no}")
    
    
    # Space before service type
    lines.append("")

    # Service Type
    if service_type:
        lines.append(service_type)

    if vehicle_name and vehicle_name not in ['', '-', 'N/A']:
        lines.append(vehicle_name)

    # Driver block (fixed order)
    if driver_name and driver_name not in ['', '-', 'N/A']:
        lines.append(driver_name)

    if driver_number and driver_number not in ['', '-', 'N/A']:
        lines.append(driver_number)

    if vehicle_number and vehicle_number not in ['', '-', 'N/A']:
        lines.append(vehicle_number)

    # Add divider (EXACTLY 48 equal signs as in example)
    lines.append("")
    lines.append("=" * 48)
    
    return "\n".join(lines)