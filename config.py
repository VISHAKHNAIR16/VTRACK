"""
Configuration and CSS styles
"""

def get_custom_css():
    """Return custom CSS styles for corporate look."""
    return """
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
        white-space: pre-wrap;
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
        max-width: 900px;
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
    """

def get_copy_js():
    """Return JavaScript for copy functionality."""
    return """
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
    """