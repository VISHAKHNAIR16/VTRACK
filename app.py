"""
Main Streamlit application
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from config import get_custom_css, get_copy_js
from utils import create_metric_card, html_preserve_text
from data_processor import process_excel_file, group_shared_services
from formatter import get_pickup_time_for_sorting, create_card_text, create_shared_card_text
import warnings

warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="VTRACK -- By Vayoaura",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


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


def display_metrics(grouped_records):
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
    
    col2, col1, col3, col4 = st.columns(4)
    
    with col2:
        st.markdown(create_metric_card("Total Passengers", total_passengers, "👥"), unsafe_allow_html=True)

    with col1:
        st.markdown(create_metric_card("Total Cards", total_cards, "📋"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("Individual", individual_count, "🚗"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("Shared Groups", shared_count, "👥"), unsafe_allow_html=True)


def display_cards(formatted_cards, grouped_records):
    """Display formatted cards with copy buttons."""
    if not formatted_cards:
        st.warning("No data to display. Please upload and process a file first.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📋 Formatted Cards", "📊 Original Data In Excel"])
    
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
            # Show original data table
            st.subheader("Original Data")
            
            # Display the entire DataFrame with all columns
            st.dataframe(st.session_state.df, use_container_width=True)
            
            # Show grouping information below it
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


def export_data(formatted_cards):
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


def main():
    """Main application function."""
    # Add custom CSS and JS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(get_copy_js(), unsafe_allow_html=True)
    
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
                        
                        # Group shared services
                        grouped_records = group_shared_services(df)

                        # SORT records by pickup time
                        # First, add sorting key to each record
                        for record in grouped_records:
                            record['sort_key'] = get_pickup_time_for_sorting(record)

                        # Sort grouped_records by pickup time
                        grouped_records.sort(key=lambda x: x['sort_key'])

                        # Format cards based on type (now in sorted order)
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
    
    # Display metrics and cards
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