"""
Utility functions for data cleaning and formatting
"""
import re
import pandas as pd
from datetime import datetime
from typing import Any, Dict


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


def format_pax_count(adult: int, child: int, infant: int) -> str:
    """Format passenger count EXACTLY as per requirements."""
    adult = int(adult) if pd.notna(adult) else 0
    child = int(child) if pd.notna(child) else 0
    infant = int(infant) if pd.notna(infant) else 0
    
    # Format exactly as in the example: "5PAX" or "4+2PAX" (no spaces before PAX)
    if child > 0 or infant > 0:
        if child > 0 and infant > 0:
            return f"{adult}+{child}+{infant} PAX"
        elif child > 0:
            return f"{adult}+{child} PAX"
        elif infant > 0:
            return f"{adult}+{infant} PAX"
    return f"{adult} PAX"


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


def html_preserve_text(text: str) -> str:
    """Convert text to HTML-preserved format."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace(" ", "&nbsp;")
        .replace("\n", "<br>")
    )


def create_metric_card(label: str, value, icon: str = "📊"):
    """Create a styled metric card."""
    return f"""
    <div class="metric-card">
        <div style="font-size: 24px; margin-bottom: 5px; color: #4a6fa5;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM time string to minutes."""
    if not time_str or ':' not in time_str:
        return 0
    
    try:
        hours, minutes = time_str.split(':')[:2]
        return int(hours) * 60 + int(minutes[:2])
    except:
        return 0


def are_times_similar(time1, time2, max_diff_minutes=30):
    """Check if two times are within specified minutes."""
    if not time1 or not time2:
        return False
    
    return abs(time_to_minutes(time1) - time_to_minutes(time2)) <= max_diff_minutes