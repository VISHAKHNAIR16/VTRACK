"""
Streamlit Travel Data Formatter
Converts Excel travel data to exact text format matching operations sheets.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import warnings
import textwrap

warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Travel Data Formatter",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for corporate look
def add_custom_css():
    """Add custom CSS styles for corporate look."""
    st.markdown("""
    <style>
    /* Corporate color scheme - dark theme */
    :root {
        --primary-color: #1e3a5f;
        --secondary-color: #2d4b8a;
        --accent-color: #4a6fa5;
        --background-color: #0f172a;
        --card-bg: #1e293b;
        --border-color: #334155;
        --text-color: #e2e8f0;
        --text-light: #94a3b8;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
        background-color: var(--background-color);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid var(--border-color);
    }
    
    /* Data card styling - EXACT TEXT FORMAT */
    .data-card {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border-left: 4px solid var(--accent-color);
        font-family: 'Courier New', monospace;
        color: var(--text-color);
        position: relative;
        white-space: pre-wrap;   /* prevents horizontal overflow */
        word-break: break-word;
        overflow-x: hidden;
        line-height: 1.4;
        font-size: 13px;
        border: 1px solid var(--border-color);
    }
    

    
    
    
    /* Card number badge */
    .card-badge {
        position: absolute;
        top: -8px;
        left: -8px;
        background: var(--accent-color);
        color: white;
        min-width: 24px;
        height: 24px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: bold;
        font-family: Arial, sans-serif;
        padding: 0 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        z-index: 10;
    }
    
    /* Card container */
    .card-container {
    background: transparent;
    padding: 5px;
    border-radius: 8px;
    margin: 20px auto;
    position: relative;
    max-width: 900px;     /* FIXED CONTENT WIDTH */
    width: 100%;
    }

    
    /* Status messages */
    .stSuccess {
        background-color: #064e3b !important;
        color: #a7f3d0 !important;
        border: 1px solid #065f46 !important;
        border-left: 4px solid var(--success-color) !important;
    }
    
    .stError {
        background-color: #7f1d1d !important;
        color: #fecaca !important;
        border: 1px solid #991b1b !important;
        border-left: 4px solid var(--error-color) !important;
    }
    
    .stWarning {
        background-color: #78350f !important;
        color: #fde68a !important;
        border: 1px solid #92400e !important;
        border-left: 4px solid var(--warning-color) !important;
    }
    
    .stInfo {
        background-color: #1e3a8a !important;
        color: #bfdbfe !important;
        border: 1px solid #1e40af !important;
        border-left: 4px solid var(--accent-color) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        border: 2px dashed #475569;
        border-radius: 8px;
        background: var(--card-bg);
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: var(--accent-color);
        background: #1e293b;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: var(--text-color);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--card-bg);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 12px;
        color: var(--text-light);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-color);
        margin: 5px 0;
    }
    
    
    /* Export section */
    .export-box {
        background: #1e3a5f;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #2d4b8a;
        margin: 15px 0;
    }
    
    /* Divider line */
    .divider-line {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
        margin: 20px 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--card-bg);
        border-radius: 6px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        color: var(--text-light);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color) !important;
        color: white !important;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 6px;
        border: 1px solid var(--border-color);
        background: var(--card-bg) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--accent-color);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: var(--card-bg);
        color: var(--text-color);
        border-color: var(--border-color);
    }
    
    .stSelectbox > div > div {
        background: var(--card-bg);
        color: var(--text-color);
        border-color: var(--border-color);
    }
    
    .stSlider > div > div > div {
        background: var(--accent-color);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .data-card {
            font-size: 12px;
            padding: 15px;
        }
        
        .metric-value {
            font-size: 20px;
        }
        
        
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'formatted_cards' not in st.session_state:
        st.session_state.formatted_cards = []
    if 'grouped_records' not in st.session_state:
        st.session_state.grouped_records = []
    if 'original_columns' not in st.session_state:
        st.session_state.original_columns = []
    if 'processing_done' not in st.session_state:
        st.session_state.processing_done = False
    if 'copy_states' not in st.session_state:
        st.session_state.copy_states = {}

def clean_phone_number(phone: str) -> str:
    """Clean and format phone numbers with EXACT spacing as in example."""
    if pd.isna(phone) or phone is None:
        return ""
    
    phone_str = str(phone).strip()
    
    # Remove country code text
    phone_str = re.sub(r'(?i)(india|ind)\s*', '', phone_str)
    phone_str = re.sub(r'[^\d\s\+]', '', phone_str)
    phone_str = phone_str.strip()
    
    # Format as +91 XXXXX XXXXX (EXACT format from example)
    if phone_str and phone_str.replace('+', '').replace(' ', '').isdigit():
        digits = re.sub(r'[^\d]', '', phone_str)
        if digits.startswith('91') and len(digits) >= 12:
            # Format: +91 XXXXX XXXXX
            phone_str = f"+91 {digits[2:7]} {digits[7:]}"
        elif len(digits) == 10:
            # Format: +91 XXXXX XXXXX
            phone_str = f"+91 {digits[:5]} {digits[5:]}"
        elif len(digits) == 12:
            phone_str = f"+{digits[:2]} {digits[2:7]} {digits[7:]}"
    
    return phone_str

def format_pax_count(adult: int, child: int, infant: int) -> str:
    """Format passenger count EXACTLY as per requirements."""
    adult = int(adult) if pd.notna(adult) else 0
    child = int(child) if pd.notna(child) else 0
    infant = int(infant) if pd.notna(infant) else 0
    
    # Format exactly as in the example: "5PAX" or "4+2PAX" (no spaces before PAX)
    if child > 0 or infant > 0:
        if child > 0 and infant > 0:
            return f"{adult}+{child}+{infant}PAX"
        elif child > 0:
            return f"{adult}+{child}PAX"
        elif infant > 0:
            return f"{adult}+{infant}PAX"
    return f"{adult} PAX"

def format_date(date_val: Any) -> str:
    """Format date in DD-MMM-YY format with EXACT spacing."""
    if pd.isna(date_val):
        return ""
    
    try:
        # Try pandas parser first
        dt = pd.to_datetime(date_val, errors='coerce')
        if pd.notna(dt):
            return dt.strftime("%d-%b-%y").upper()
        
        # Try string parsing
        date_str = str(date_val).strip()
        # Remove any non-date characters
        date_str = re.sub(r'[^\d/\-\.]', '', date_str)
        
        for fmt in ['%d-%b-%y', '%d/%b/%y', '%d-%b-%Y', '%d/%b/%Y', 
                   '%d-%m-%y', '%d/%m/%y', '%d-%m-%Y', '%d/%m/%Y',
                   '%Y-%m-%d', '%Y/%m/%d']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d-%b-%y").upper()
            except:
                continue
    except:
        pass
    
    return str(date_val)

def clean_name(name: str) -> str:
    """Clean guest names with proper spacing."""
    if pd.isna(name) or name is None:
        return ""
    
    name_str = str(name).strip()
    name_str = re.sub(r'\s+', ' ', name_str)
    
    # Fix common title issues
    if name_str.upper().startswith('MR.'):
        name_str = 'Mr.' + name_str[3:]
    elif name_str.upper().startswith('MRS.'):
        name_str = 'Mrs.' + name_str[4:]
    elif name_str.upper().startswith('MS.'):
        name_str = 'Ms.' + name_str[3:]
    
    return name_str

def clean_flight_number(flight_no: str) -> str:
    """Clean flight number WITHOUT destroying spacing or line breaks."""
    if pd.isna(flight_no) or not flight_no:
        return ""

    flight_str = str(flight_no).strip()

    # Remove unwanted characters but KEEP spacing and newlines
    flight_str = re.sub(r'[^\w\s\-]', '', flight_str)

    # Remove known invalid placeholders
    if flight_str.strip() in ['', '-', 'N/A', 'NA']:
        return ""

    return flight_str

def group_shared_services(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Group passengers who share the same vehicle/driver for tours.
    SMART GROUPING: Groups by vehicle/driver first, then checks for similarity.
    """
    grouped_records = []
    
    # Make a copy
    temp_df = df.copy()
    
    # Clean and standardize time format
    def clean_time(time_val):
        if pd.isna(time_val):
            return ""
        time_str = str(time_val).strip()
        # Remove seconds if present
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) >= 2:
                return f"{parts[0].zfill(2)}:{parts[1][:2].zfill(2)}"
        return time_str
    
    temp_df['CleanPickupTime'] = temp_df['PickupTime'].apply(clean_time)
    
    # Clean vehicle/driver info
    def clean_vehicle_info(val):
        if pd.isna(val):
            return ""
        return str(val).strip()
    
    temp_df['CleanVehicleName'] = temp_df['VehicalName'].apply(clean_vehicle_info)
    temp_df['CleanDriverName'] = temp_df['Driver Name'].apply(clean_vehicle_info)
    temp_df['CleanDriverNumber'] = temp_df['Driver Number'].apply(clean_vehicle_info)
    temp_df['CleanVehicleNumber'] = temp_df['Vehicle Number'].apply(clean_vehicle_info)
    
    # STEP 1: Identify TOURS
    is_tour = (
        (temp_df['ProductType'].str.strip().str.upper() == 'TOUR') |
        (temp_df['ServiceType'].str.strip().str.upper().str.contains('TOUR'))
    )
    
    tour_df = temp_df[is_tour].copy()
    non_tour_df = temp_df[~is_tour]
    
    # Process non-tour rows as individual
    for _, row in non_tour_df.iterrows():
        grouped_records.append({
            'type': 'individual',
            'data': row.to_dict(),
            'row_index': row.name if hasattr(row, 'name') else _
        })
    
    # STEP 2: Process tours
    if not tour_df.empty:
        # Separate SHARING and PRIVATE tours
        sharing_mask = tour_df['ServiceType'].str.strip().str.upper() == 'SHARING'
        sharing_tours = tour_df[sharing_mask]
        private_tours = tour_df[~sharing_mask]
        
        # Process PRIVATE tours as individual
        for _, row in private_tours.iterrows():
            grouped_records.append({
                'type': 'individual',
                'data': row.to_dict(),
                'row_index': row.name
            })
        
        # STEP 3: SMART GROUPING for SHARING tours
        if not sharing_tours.empty:
            # First, try to group by VEHICLE/DRIVER info
            # Create a vehicle group key
            sharing_tours['VehicleGroupKey'] = sharing_tours.apply(
                lambda x: (
                    format_date(x.get('ServiceDate', '')),
                    x['CleanVehicleName'],
                    x['CleanDriverName'],
                    x['CleanDriverNumber'],
                    x['CleanVehicleNumber']
                ),
                axis=1
            )
            
            # Process each vehicle group
            processed_indices = set()
            
            for vehicle_key, vehicle_group in sharing_tours.groupby('VehicleGroupKey'):
                # Check if this vehicle has valid info
                first_row = vehicle_group.iloc[0]
                has_vehicle_info = (
                    first_row['CleanVehicleName'] not in ['', '-', 'N/A'] and
                    first_row['CleanDriverName'] not in ['', '-', 'N/A']
                )
                
                if has_vehicle_info and len(vehicle_group) > 1:
                    # This vehicle has multiple passengers - group them
                    process_sharing_group(vehicle_group, grouped_records)
                    processed_indices.update(vehicle_group.index.tolist())
                elif len(vehicle_group) == 1:
                    # Single passenger with vehicle info - check for time-based grouping
                    row = vehicle_group.iloc[0]
                    # We'll handle this in the next step
                    pass
                else:
                    # Multiple passengers but no vehicle info - need time/location grouping
                    # We'll handle this in the next step
                    pass
            
            # STEP 4: Group remaining passengers by TIME and SERVICE SIMILARITY
            remaining = sharing_tours[~sharing_tours.index.isin(processed_indices)]
            
            if not remaining.empty:
                # Group by date and similar time window
                remaining['TimeGroupKey'] = remaining.apply(
                    lambda x: (
                        format_date(x.get('ServiceDate', '')),
                        # Group by hour (e.g., 08:10 and 08:20 both become "08")
                        x['CleanPickupTime'].split(':')[0] if ':' in x['CleanPickupTime'] else '',
                        # Normalize service name for grouping
                        normalize_service_name(x.get('ServiceName', ''))
                    ),
                    axis=1
                )
                
                for time_key, time_group in remaining.groupby('TimeGroupKey'):
                    if len(time_group) > 1:
                        # Group by similar pickup time (within 30 minutes)
                        time_groups = group_by_time_window(time_group, time_window_minutes=30)
                        for group in time_groups:
                            if len(group) > 1:
                                group_df = pd.DataFrame(group)
                                process_sharing_group(group_df, grouped_records)
                            else:
                                # Single passenger in time window
                                row = group[0]
                                grouped_records.append({
                                    'type': 'individual',
                                    'data': row,
                                    'row_index': row.name if hasattr(row, 'name') else None
                                })
                    else:
                        # Single passenger
                        row = time_group.iloc[0]
                        grouped_records.append({
                            'type': 'individual',
                            'data': row.to_dict(),
                            'row_index': row.name
                        })
    
    return grouped_records

def normalize_service_name(service_name: str) -> str:
    """Normalize service name for grouping (remove variations)."""
    if not service_name:
        return ""
    
    service = str(service_name).upper()
    
    # Remove common prefixes/suffixes
    service = re.sub(r'^\s*(NO\s+KIDDING\s*)?', '', service, flags=re.IGNORECASE)
    service = re.sub(r'\s*(XRQT|TOUR|PACKAGE|WITH\s+LUNCH).*$', '', service, flags=re.IGNORECASE)
    
    # Keep only alphanumeric characters
    service = re.sub(r'[^A-Z0-9\s]', '', service)
    
    return service.strip()

def group_by_time_window(df_group, time_window_minutes=30):
    """
    Group rows by time windows.
    """
    if len(df_group) <= 1:
        return [df_group.to_dict('records')]
    
    # Convert to list of rows
    rows = df_group.to_dict('records')
    
    # Sort by pickup time
    rows.sort(key=lambda x: time_to_minutes(x.get('PickupTime', '')))
    
    groups = []
    current_group = []
    
    for row in rows:
        if not current_group:
            current_group.append(row)
        else:
            last_time = time_to_minutes(current_group[-1].get('PickupTime', ''))
            current_time = time_to_minutes(row.get('PickupTime', ''))
            
            if abs(current_time - last_time) <= time_window_minutes:
                current_group.append(row)
            else:
                groups.append(current_group)
                current_group = [row]
    
    if current_group:
        groups.append(current_group)
    
    return groups

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM time string to minutes."""
    if not time_str or ':' not in time_str:
        return 0
    
    try:
        hours, minutes = time_str.split(':')[:2]
        return int(hours) * 60 + int(minutes[:2])
    except:
        return 0

def process_sharing_group(group_df, grouped_records):
    """Helper function to process a sharing group."""
    group_passengers = []
    
    for _, row in group_df.iterrows():
        row_dict = row.to_dict()
        
        passenger_info = {
            'pnr': str(row.get('PNR', '')).strip(),
            'leg_id': str(row.get('LegId', '')).strip(),
            'guest_name': clean_name(row.get('GuestName', '')),
            'whatsapp_no': clean_phone_number(row.get('WhatsappNo', '')),
            'alternate_no': clean_phone_number(row.get('AlternateNumber', '')),
            'adult': int(row.get('Adult', 0)) if pd.notna(row.get('Adult')) else 0,
            'child': int(row.get('Child', 0)) if pd.notna(row.get('Child')) else 0,
            'infant': int(row.get('Infant', 0)) if pd.notna(row.get('Infant')) else 0,
            'transfer_from': str(row.get('TransferFrom', '')).strip(),
            'transfer_to': str(row.get('TransferTo', '')).strip(),
            'service_name': str(row.get('ServiceName', '')).strip(),
            'tour_option_name': str(row.get('TourOptionName', '')).strip(),
            'pickup_time': clean_time(row.get('PickupTime', '')),
            'row_index': row.name if hasattr(row, 'name') else _,
            'row_data': row_dict  # Store the complete row data
        }
        group_passengers.append(passenger_info)
    
    # Get common data from first row in group
    first_row = group_df.iloc[0]
    group_data = {
        'type': 'shared',
        'passengers': group_passengers,
        'common_data': {
            'service_date': format_date(first_row.get('ServiceDate', '')),
            'service_type': str(first_row.get('ServiceType', '')).strip(),
            'vehicle_name': str(first_row.get('VehicleName', '')).strip(),
            'driver_name': str(first_row.get('Driver Name', '')).strip(),
            'driver_number': str(first_row.get('Driver Number', '')).strip(),
            'vehicle_number': str(first_row.get('Vehicle Number', '')).strip()
        }
    }
    grouped_records.append(group_data)

def clean_time(time_val):
    """Clean and format time."""
    if pd.isna(time_val):
        return ""
    time_str = str(time_val).strip()
    # Remove seconds if present
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1][:2].zfill(2)}"
    return time_str

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
                pax_str = f"{adult}+{child}+{infant}PAX"
            elif child > 0:
                pax_str = f"{adult}+{child}PAX"
            elif infant > 0:
                pax_str = f"{adult}+{infant}PAX"
        else:
            pax_str = f"{adult}PAX"
        
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
            # Clean service text
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
    # Vehicle name first
    if common['vehicle_name'] and common['vehicle_name'].strip() not in ['', '-', 'N/A', 'UNKNOWN_VEHICLE']:
        lines.append(common['vehicle_name'])
    
    # Driver name
    if common['driver_name'] and common['driver_name'].strip() not in ['', '-', 'N/A', 'UNKNOWN_DRIVER']:
        lines.append(common['driver_name'])
    
    # Driver number
    if common['driver_number'] and common['driver_number'].strip() not in ['', '-', 'N/A']:
        lines.append(common['driver_number'])
    
    # Vehicle number
    if common['vehicle_number'] and common['vehicle_number'].strip() not in ['', '-', 'N/A', 'UNKNOWN_VEHICLE_NUM']:
        lines.append(common['vehicle_number'])
    
    # Add divider
    lines.append("")
    lines.append("=" * 48)
    
    return "\n".join(lines)

def create_card_text(row: Dict[str, Any]) -> str:
    """Create formatted text for a single card in EXACT format as per requirements."""
    # Extract with safe defaults
    pnr = str(row.get('PNR', '')).strip()
    leg_id = str(row.get('LegId', '')).strip()
    guest_name = clean_name(row.get('GuestName', ''))
    whatsapp_no = clean_phone_number(row.get('WhatsappNo', ''))
    alternate_no = clean_phone_number(row.get('AlternateNumber', ''))
    
    # Get service name - try TourOptionName first, then ServiceName
    
    service_name = str(row.get('ServiceName', '')).strip()
    
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


def should_group_passengers(row1, row2):
    """Determine if two passengers should be grouped."""
    # Same date
    if format_date(row1.get('ServiceDate')) != format_date(row2.get('ServiceDate')):
        return False
    
    # Same or similar service name
    service1 = str(row1.get('ServiceName', '')).strip()[:20]
    service2 = str(row2.get('ServiceName', '')).strip()[:20]
    if service1 != service2:
        return False
    
    # Same or similar pickup time (within 30 minutes)
    time1 = clean_time(row1.get('PickupTime', ''))
    time2 = clean_time(row2.get('PickupTime', ''))
    if not are_times_similar(time1, time2, max_diff_minutes=30):
        return False
    
    # Both marked as Sharing
    if (row1.get('ServiceType', '').strip().upper() != 'SHARING' or 
        row2.get('ServiceType', '').strip().upper() != 'SHARING'):
        return False
    
    return True

def are_times_similar(time1, time2, max_diff_minutes=30):
    """Check if two times are within specified minutes."""
    if not time1 or not time2:
        return False
    
    def to_minutes(t):
        try:
            h, m = t.split(':')[:2]
            return int(h) * 60 + int(m[:2])
        except:
            return 0
    
    return abs(to_minutes(time1) - to_minutes(time2)) <= max_diff_minutes

def html_preserve_text(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace(" ", "&nbsp;")
        .replace("\n", "<br>")
    )


def process_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Process uploaded Excel file with improved error handling.
    """
    try:
        # Show processing status
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        status_text.text("📂 Reading Excel file...")
        progress_bar.progress(20)
        
        # Read Excel file
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl', dtype=str)
        elif uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd', dtype=str)
        else:
            st.error("❌ Please upload an Excel file (.xlsx or .xls)")
            return None
        
        status_text.text("🔄 Processing columns...")
        progress_bar.progress(40)
        
        # Store original columns
        st.session_state.original_columns = df.columns.tolist()
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Standardize column names (case-insensitive mapping)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower().replace(' ', '').replace('_', '').replace('-', '')
            
            # Map based on common patterns
            if 'pnr' in col_lower:
                column_mapping[col] = 'PNR'
            elif 'legid' in col_lower or 'leg' in col_lower:
                column_mapping[col] = 'LegId'
            elif 'guestname' in col_lower or 'guest' in col_lower:
                column_mapping[col] = 'GuestName'
            elif 'whatsappno' in col_lower or 'whatsapp' in col_lower:
                column_mapping[col] = 'WhatsappNo'
            elif 'alternatenumber' in col_lower or 'alternate' in col_lower:
                column_mapping[col] = 'AlternateNumber'
            elif 'servicename' in col_lower:
                column_mapping[col] = 'ServiceName'
            elif 'transferfrom' in col_lower:
                column_mapping[col] = 'TransferFrom'
            elif 'transferto' in col_lower:
                column_mapping[col] = 'TransferTo'
            elif 'adult' in col_lower:
                column_mapping[col] = 'Adult'
            elif 'child' in col_lower:
                column_mapping[col] = 'Child'
            elif 'infant' in col_lower:
                column_mapping[col] = 'Infant'
            elif 'servicedate' in col_lower:
                column_mapping[col] = 'ServiceDate'
            elif 'servicetype' in col_lower:
                column_mapping[col] = 'ServiceType'
            elif 'transfertype' in col_lower:
                column_mapping[col] = 'TransferType'
            elif 'pickuptime' in col_lower or 'pickup' in col_lower:
                column_mapping[col] = 'PickupTime'
            elif 'flightno' in col_lower or 'flightNo' in col_lower:
                column_mapping[col] = 'FlightNo'
            elif 'vehicalname' in col_lower or 'vehiclename' in col_lower:
                column_mapping[col] = 'VehicalName'
            elif 'drivername' in col_lower:
                column_mapping[col] = 'Driver Name'
            elif ('driver' in col_lower and 'number' in col_lower) or 'drivermobile' in col_lower:
                column_mapping[col] = 'Driver Number'
            elif ('vehicle' in col_lower and 'number' in col_lower) or 'vehicle number' in col_lower:
                column_mapping[col] = 'Vehicle Number'
            elif 'touroptionname' in col_lower or 'touroption' in col_lower:
                column_mapping[col] = 'TourOptionName'
            elif 'transfername' in col_lower:
                column_mapping[col] = 'TransferName'
            elif 'remarks' in col_lower:
                column_mapping[col] = 'Remarks'
        
        # Apply column mapping
        df.rename(columns=column_mapping, inplace=True)
        
        status_text.text("✨ Formatting data...")
        progress_bar.progress(60)
        
        # Fill missing columns with empty strings
        required_columns = [
            'PNR', 'LegId', 'GuestName', 'WhatsappNo', 'AlternateNumber',
            'ServiceName', 'TransferFrom', 'TransferTo', 'Adult', 'Child', 
            'Infant', 'ServiceDate', 'ServiceType', 'TransferType', 
            'PickupTime', 'FlightNo', 'VehicalName', 'Driver Name', 
            'Driver Number', 'Vehicle Number', 'TourOptionName', 'TransferName'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Convert numeric columns
        for col in ['Adult', 'Child', 'Infant']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Fill all NaN values with empty string
        df = df.fillna("")
        
        status_text.text("🎯 Finalizing...")
        progress_bar.progress(80)
        
        st.success(f"✅ Successfully loaded {len(df)} records")
        
        # Display column information
        with st.expander("📊 Column Information", expanded=False):
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Non-Empty Values': [df[col].astype(bool).sum() for col in df.columns],
                'Sample Value': [df[col].iloc[0] if len(df) > 0 else '' for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Add delay before clearing progress
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error processing Excel file: {str(e)}")
        st.info("💡 **Troubleshooting tips:**")
        st.info("1. Make sure all columns in Excel have proper headers")
        st.info("2. Check that there are no merged cells in the header row")
        st.info("3. Try saving the Excel file as .xlsx format")
        return None

def create_metric_card(label: str, value, icon: str = "📊"):
    """Create a styled metric card."""
    return f"""
    <div class="metric-card">
        <div style="font-size: 24px; margin-bottom: 5px; color: #4a6fa5;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def display_metrics(grouped_records: List[Dict[str, Any]]):
    """Display metrics about the data considering grouped records."""
    if not grouped_records:
        return
    
    total_cards = len(grouped_records)
    
    # Count individual vs shared
    individual_count = sum(1 for r in grouped_records if r['type'] == 'individual')
    shared_count = sum(1 for r in grouped_records if r['type'] == 'shared')
    
    # Count total passengers
    total_passengers = 0
    for record in grouped_records:
        if record['type'] == 'individual':
            total_passengers += 1
        else:
            total_passengers += len(record['passengers'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Total Cards", total_cards, "📋"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("Total Passengers", total_passengers, "👥"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("Individual", individual_count, "🚗"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("Shared Groups", shared_count, "👥"), unsafe_allow_html=True)


def display_cards(formatted_cards: List[str], grouped_records: List[Dict[str, Any]]):
    """Display formatted cards with copy buttons."""
    if not formatted_cards:
        st.warning("No data to display. Please upload and process a file first.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📋 Formatted Cards", "📊 Grouped Data Preview"])
    
    with tab1:
        # Display cards with copy buttons
        for i, card_text in enumerate(formatted_cards):
            if i < len(formatted_cards):
                # Determine card type for badge
                card_type = grouped_records[i]['type'] if i < len(grouped_records) else 'individual'
                badge_color = "#4a6fa5" if card_type == 'individual' else "#10b981"
                
                card_html = f"""
                <div class="card-container">
                    <div class="card-badge" style="background: {badge_color};">#{i + 1}</div>
                    <div class="data-card">{html_preserve_text(card_text)}</div>
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.df is not None:
            # Show grouping information
            st.subheader("Grouping Summary")
            
            group_info = []
            for i, record in enumerate(grouped_records):
                if record['type'] == 'shared':
                    group_info.append({
                        'Card #': i + 1,
                        'Type': 'Shared',
                        'Passengers': len(record['passengers']),
                        'Vehicle': record['common_data'].get('vehicle_name', 'N/A'),
                        'Driver': record['common_data'].get('driver_name', 'N/A'),
                        'Pickup Time': record['common_data'].get('pickup_time', 'N/A')
                    })
            
            if group_info:
                st.dataframe(pd.DataFrame(group_info), use_container_width=True)
            else:
                st.info("No shared groups found in the data")

def export_data(formatted_cards: List[str]):
    """Provide export options."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        
        if formatted_cards:
            # Combine all cards
            all_text = "\n\n".join(formatted_cards)
            
            # Get date for filename
            date_str = datetime.now().strftime("%d-%b-%y")
            filename = f"Travel_Bookings_{date_str}.txt"
            
            # Download button
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 TXT",
                    data=all_text,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
            
            # Show preview of first few lines
            with st.expander("📋 Preview Format", expanded=False):
                if formatted_cards:
                    st.code(formatted_cards[0], language="text")
                    st.caption("First card format preview")



def add_copy_js():
    st.markdown("""
    <script>
    function copyCardText(button) {
        const card = button.parentElement.querySelector('.data-card');
        const text = card.innerText;

        navigator.clipboard.writeText(text).then(() => {
            button.innerText = 'COPIED';
            button.classList.add('copied');
            setTimeout(() => {
                button.innerText = 'COPY';
                button.classList.remove('copied');
            }, 1500);
        });
    }
    </script>
    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    # Add custom CSS
    add_custom_css()
    add_copy_js()

    
    # Initialize session state
    initialize_session_state()
    
    # App header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2rem;">📋 Welcome To VTrack</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1rem;">
        Convert Excel travel booking data to operational text format with exact spacing
        </p>
                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1rem;">
        Please use the side panel to upload the excel sheet and the results will be shown in the main panel which is here!!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown("## 📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload your travel booking Excel file",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.info(f"📄 **File:** {uploaded_file.name}")
            
            if st.button("🔄 Process & Format Data", use_container_width=True, type="primary"):
                with st.spinner("Processing Excel file..."):
                    df = process_excel_file(uploaded_file)
                    if df is not None:
                        st.session_state.df = df
                        
                        # NEW: Group shared services
                        grouped_records = group_shared_services(df)
                        
                        # Format cards based on type
                        formatted_cards = []
                        for record in grouped_records:
                            if record['type'] == 'individual':
                                card_text = create_card_text(record['data'])
                            else:  # shared
                                card_text = create_shared_card_text(record)
                            formatted_cards.append(card_text)
                        
                        st.session_state.formatted_cards = formatted_cards
                        st.session_state.grouped_records = grouped_records  # Store for reference
                        st.session_state.processing_done = True
                        st.success("✅ Data processed successfully!")
                        st.rerun()
    
    # In main() function, find where display_metrics is called:
    if st.session_state.df is not None and st.session_state.formatted_cards:
        # Display metrics - pass grouped_records instead of df
        st.markdown("### 📊 Overview")
        if 'grouped_records' in st.session_state:
            display_metrics(st.session_state.grouped_records)
        
        st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
        
        # Display cards - pass grouped_records
        st.markdown("### 📋 Formatted Cards")
        display_cards(
            st.session_state.formatted_cards,
            st.session_state.grouped_records
        )

        # Sidebar export options
    if st.session_state.formatted_cards:
        export_data(st.session_state.formatted_cards)

        
        
        

if __name__ == "__main__":
    main()