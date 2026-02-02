"""
Data processing and grouping logic
"""
import pandas as pd
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from utils import format_date, clean_time, time_to_minutes, clean_name, clean_phone_number


def normalize_service_name(service_name: str) -> str:
    """Normalize service name for grouping (remove variations)."""
    if not service_name:
        return ""
    
    service = str(service_name)
    
    # Remove common prefixes/suffixes
    service = re.sub(r'^\s*(NO\s+KIDDING\s*)?', '', service, flags=re.IGNORECASE)
    service = re.sub(r'\s*(TOUR|PACKAGE|WITH\s+LUNCH).*$', '', service, flags=re.IGNORECASE)
    
    # Remove XRQT specifically and clean up surrounding text
    service = re.sub(r'\s*XRQT\s*', ' ', service, flags=re.IGNORECASE)
    
    # Clean up any extra spaces created by removing XRQT
    service = re.sub(r'\s+', ' ', service)
    
    # Remove any trailing "WITH" that might be left after removing XRQT
    service = re.sub(r'\s+WITH$', '', service, flags=re.IGNORECASE)
    
    # Keep only alphanumeric characters and spaces
    service = re.sub(r'[^A-Za-z0-9\s]', '', service)
    
    return service.strip()


def group_by_time_window(df_group, time_window_minutes=45):
    """
    Group rows by time windows (true sliding: any row in group <= window).
    """
    if len(df_group) <= 1:
        return [df_group.to_dict('records')]
    
    rows = df_group.to_dict('records')
    rows.sort(key=lambda x: time_to_minutes(x.get('PickupTime', '')))
    
    groups = []
    current_group = []
    
    for row in rows:
        current_time = time_to_minutes(row.get('PickupTime', ''))
        
        if not current_group:
            current_group.append(row)
            continue
        
        # Key fix: check vs ALL in current_group
        can_join = any(
            abs(current_time - time_to_minutes(prev.get('PickupTime', ''))) <= time_window_minutes
            for prev in current_group
        )
        
        if can_join:
            current_group.append(row)
        else:
            groups.append(current_group)
            current_group = [row]
    
    if current_group:
        groups.append(current_group)
    
    return groups



def process_sharing_group(group_df, grouped_records):
    """Helper function to process a sharing group."""
    group_passengers = []
    
    # Use the minimum index from the group for sorting
    group_min_index = group_df.index.min()
    
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
    
    # Get common data - try to find ANY row with vehicle/driver info
    vehicle_name = ""
    driver_name = ""
    driver_number = ""
    vehicle_number = ""
    
    # Look through all rows to find vehicle/driver info
    for _, row in group_df.iterrows():
        temp_vehicle = str(row.get('VehicalName', '')).strip()
        temp_driver = str(row.get('Driver Name', '')).strip()
        temp_driver_num = str(row.get('Driver Number', '')).strip()
        temp_vehicle_num = str(row.get('Vehicle Number', '')).strip()
        
        if temp_vehicle and temp_vehicle not in ['', '-', 'N/A']:
            vehicle_name = temp_vehicle
        if temp_driver and temp_driver not in ['', '-', 'N/A']:
            driver_name = temp_driver
        if temp_driver_num and temp_driver_num not in ['', '-', 'N/A']:
            driver_number = temp_driver_num
        if temp_vehicle_num and temp_vehicle_num not in ['', '-', 'N/A']:
            vehicle_number = temp_vehicle_num
    
    # Get other common data from first row
    first_row = group_df.iloc[0]
    group_data = {
        'type': 'shared',
        'passengers': group_passengers,
        'common_data': {
            'service_date': format_date(first_row.get('ServiceDate', '')),
            'service_type': str(first_row.get('ServiceType', '')).strip(),
            'vehicle_name': vehicle_name,
            'driver_name': driver_name,
            'driver_number': driver_number,
            'vehicle_number': vehicle_number
        },
        'sort_index': group_min_index  # Use minimum index for sorting
    }
    grouped_records.append(group_data)


def group_shared_services(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Group passengers who share the same vehicle/driver for tours.
    Enhanced for handling data from merged cells.
    FIXED: Added time_window grouping instead of hour-only binning.
    """
    grouped_records = []
    
    # Make a copy - preserve original order
    temp_df = df.copy()
    
    # Add original index for sorting
    temp_df['OriginalIndex'] = range(len(temp_df))
    
    # Clean and standardize time format
    temp_df['CleanPickupTime'] = temp_df['PickupTime'].apply(clean_time)
    
    # Clean vehicle/driver info
    def clean_info(val):
        if pd.isna(val) or val is None:
            return ""
        cleaned = str(val).strip()
        return "" if cleaned in ['-', 'N/A', 'NA', 'n/a', 'na'] else cleaned
    
    vehicle_info_columns = ['VehicalName', 'Driver Name', 'Driver Number', 'Vehicle Number']
    for col in vehicle_info_columns:
        if col in temp_df.columns:
            temp_df[f'Clean{col}'] = temp_df[col].apply(clean_info)
    
    # STEP 1: Identify SHARING services
    is_sharing = temp_df['ServiceType'].apply(
        lambda x: str(x).strip().upper() == 'SHARING'
    )
    
    sharing_df = temp_df[is_sharing].copy()
    individual_df = temp_df[~is_sharing]
    
    # Process individual rows
    for index, row in individual_df.iterrows():
        grouped_records.append({
            'type': 'individual',
            'data': row.to_dict(),
            'row_index': index,
            'sort_index': row['OriginalIndex'] if 'OriginalIndex' in row else index
        })
    
    # STEP 2: Group sharing services - FIXED with time window
    if not sharing_df.empty:
        # FIRST: Group by vehicle/driver/service (REMOVED hour binning)
        grouping_keys = []
        for _, row in sharing_df.iterrows():
            vehicle_key = (
                format_date(row.get('ServiceDate', '')),
                row.get('CleanVehicalName', ''),
                row.get('CleanDriver Name', ''),
                row.get('CleanDriver Number', ''),
                row.get('CleanVehicle Number', ''),
                normalize_service_name(row.get('ServiceName', ''))
                # REMOVED: row.get('CleanPickupTime', '').split(':')[0] 
            )
            grouping_keys.append(vehicle_key)
        
        sharing_df['GroupKey'] = grouping_keys
        
        # Process each vehicle/service group
        for group_key, group_df in sharing_df.groupby('GroupKey'):
            group_df = group_df.sort_values('OriginalIndex')
            
            if len(group_df) > 0:
                first_row = group_df.iloc[0]
                has_vehicle_info = (
                    first_row['CleanVehicalName'] not in ['', '-', 'N/A'] and
                    first_row['CleanDriver Name'] not in ['', '-', 'N/A']
                )
                
                # FIXED: Apply time_window grouping WITHIN each vehicle group
                time_subgroups = group_by_time_window(group_df.reset_index(drop=True), time_window_minutes=45)
                
                for subgroup_df_list in time_subgroups:
                    subgroup_df = pd.DataFrame(subgroup_df_list)
                    
                    if len(subgroup_df) > 1:
                        # Multiple passengers in time window -> shared group
                        group_passengers = []
                        
                        for _, row in subgroup_df.iterrows():
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
                                'row_data': row.to_dict()
                            }
                            group_passengers.append(passenger_info)
                        
                        # Get common data from first row
                        group_data = {
                            'type': 'shared',
                            'passengers': group_passengers,
                            'common_data': {
                                'service_date': format_date(first_row.get('ServiceDate', '')),
                                'service_type': str(first_row.get('ServiceType', '')).strip(),
                                'vehicle_name': first_row['CleanVehicalName'],
                                'driver_name': first_row['CleanDriver Name'],
                                'driver_number': first_row['CleanDriver Number'],
                                'vehicle_number': first_row['CleanVehicle Number'],
                                'service_name': str(first_row.get('ServiceName', '')).strip(),
                                'pickup_time': clean_time(first_row.get('PickupTime', '')),
                                'group_size': len(subgroup_df)
                            },
                            'sort_index': subgroup_df['OriginalIndex'].min()
                        }
                        grouped_records.append(group_data)
                    else:
                        # Single passenger in time window
                        row = subgroup_df.iloc[0]
                        grouped_records.append({
                            'type': 'individual',
                            'data': row.to_dict(),
                            'row_index': row.name if hasattr(row, 'name') else index,
                            'sort_index': row['OriginalIndex'] if 'OriginalIndex' in row else index
                        })
    
    # Sort all records by their original order
    grouped_records.sort(key=lambda x: x.get('sort_index', 999999))
    
    return grouped_records


def process_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Process uploaded Excel file with special handling for merged cells.
    Merged cells in sharing groups typically have vehicle/driver info only in the first row.
    """
    import streamlit as st
    import pandas as pd
    import numpy as np
    
    try:
        # Show processing status
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        status_text.text("📂 Reading Excel file with merged cell handling...")
        progress_bar.progress(20)
        
        # Read Excel file
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl', dtype=str, header=0)
        elif uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd', dtype=str, header=0)
        else:
            st.error("❌ Please upload an Excel file (.xlsx or .xls)")
            return None
        
        status_text.text("🔄 Handling merged cells...")
        progress_bar.progress(40)
        
        # Store original columns
        st.session_state.original_columns = df.columns.tolist()
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Standardize column names (same as before)
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
            elif 'vehicalname' in col_lower or 'VehicalName' in col_lower:
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
        
        status_text.text("🔍 Detecting and filling merged cells...")
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
        
        # CRITICAL: Handle merged cells by forward-filling vehicle/driver info
        # This assumes that when vehicle/driver info is in merged cells,
        # the first row of the group has the info and subsequent rows are empty
        vehicle_info_columns = ['VehicalName', 'Driver Name', 'Driver Number', 'Vehicle Number']
        
        for col in vehicle_info_columns:
            if col in df.columns:
                # Forward fill only non-empty values (skip NaN/empty strings)
                mask = (df[col].notna()) & (df[col] != '') & (df[col] != ' ') & (df[col] != '-')
                df[col] = df[col].where(mask).ffill()
        
        # Also forward fill other common grouping columns
        grouping_columns = ['ServiceName', 'ServiceDate', 'PickupTime', 'ServiceType', 'TourOptionName']
        for col in grouping_columns:
            if col in df.columns:
                mask = (df[col].notna()) & (df[col] != '') & (df[col] != ' ') & (df[col] != '-')
                df[col] = df[col].where(mask).ffill()
        
        # Convert numeric columns
        for col in ['Adult', 'Child', 'Infant']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Fill all remaining NaN values with empty string
        df = df.fillna("")
        
        status_text.text("✨ Formatting and sorting data...")
        progress_bar.progress(80)
        
        # Sort the dataframe by pickup time
        def time_to_sortable(t):
            if pd.isna(t) or not t or str(t).strip() == '':
                return "99:99"
            time_str = str(t).strip()
            if ':' in time_str:
                parts = time_str.split(':')
                hours = parts[0].zfill(2)
                minutes = parts[1][:2].zfill(2) if len(parts) > 1 else "00"
                return f"{hours}:{minutes}"
            elif len(time_str) == 4 and time_str.replace(':', '').isdigit():
                return f"{time_str[:2]}:{time_str[2:]}"
            else:
                try:
                    # Try to parse as float (Excel time)
                    time_val = float(time_str)
                    hours = int(time_val * 24)
                    minutes = int((time_val * 24 * 60) % 60)
                    return f"{hours:02d}:{minutes:02d}"
                except:
                    return "99:99"
        
        # Add sortable time column
        df['SortableTime'] = df['PickupTime'].apply(time_to_sortable)
        
        # Sort by date first, then by time
        df['SortableDate'] = pd.to_datetime(df['ServiceDate'], errors='coerce')
        
        # Sort DataFrame by Date, then Time
        df = df.sort_values(['SortableDate', 'SortableTime'])
        
        # Remove temporary columns
        df = df.drop(columns=['SortableTime', 'SortableDate'])
        
        status_text.text("✅ Finalizing processing...")
        progress_bar.progress(95)
        
        st.success(f"✅ Successfully loaded {len(df)} records with merged cell handling")
        
        # Display preview of processed data
        with st.expander("👁️ Preview Processed Data", expanded=False):
            st.write("First 10 rows after handling merged cells:")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show vehicle/driver info distribution
            st.write("Vehicle/Driver Info Distribution:")
            vehicle_stats = pd.DataFrame({
                'Column': vehicle_info_columns,
                'Non-Empty Values': [df[col].astype(bool).sum() for col in vehicle_info_columns if col in df.columns]
            })
            st.dataframe(vehicle_stats, use_container_width=True)
        
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
        st.exception(e)
        return None