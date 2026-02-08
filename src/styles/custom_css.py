"""
Cyberpunk/Premium Theme for Streamlit
A modern, futuristic design with glassmorphism effects and neon accents.
"""

def get_custom_css():
    """
    Returns custom CSS string for Cyberpunk/Premium Streamlit theme.
    
    Features:
    - Glassmorphism cards with backdrop blur
    - Neon green (#00FF94) and cyber blue (#00E5FF) accents
    - Animated gradient background
    - Rounded corners (15px)
    - Hidden Streamlit header and footer
    """
    return """
        <style>
        /* ============================================
           ANIMATED GRADIENT BACKGROUND
           ============================================ */
        .stApp {
            background: linear-gradient(
                135deg,
                #0a0e27 0%,
                #1a1f3a 25%,
                #0f1419 50%,
                #1e1e2e 75%,
                #0a0e27 100%
            );
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #ffffff;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* ============================================
           HIDE STREAMLIT CRUFT
           ============================================ */
        /* Hide top header decoration */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Hide footer */
        footer {
            display: none !important;
        }
        
        /* Hide "Deploy" button and menu */
        .css-1dp5vir, .css-164nlkn {
            display: none !important;
        }
        
        /* ============================================
           GLASSMORPHISM METRIC CARDS
           ============================================ */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 25px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stMetric"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(0, 255, 148, 0.3) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 40px 0 rgba(0, 255, 148, 0.2) !important;
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            color: #00FF94 !important;
            text-shadow: 0 0 20px rgba(0, 255, 148, 0.5) !important;
            overflow: visible !important;
            white-space: nowrap !important;
            text-overflow: clip !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.8) !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            overflow: visible !important;
            white-space: normal !important;
        }
        
        div[data-testid="stMetricDelta"] {
            color: #00E5FF !important;
            overflow: visible !important;
            white-space: nowrap !important;
        }
        
        /* ============================================
           GLASSMORPHISM CONTAINERS
           ============================================ */
        div.stContainer,
        div[data-testid="stContainer"],
        div[data-testid="stVerticalBlock"] > div[style*="padding"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 20px !important;
        }
        
        /* ============================================
           NEON BUTTONS
           ============================================ */
        div.stButton > button {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%) !important;
            color: #0a0e27 !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 0 20px rgba(0, 255, 148, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:hover {
            background: linear-gradient(135deg, #00E5FF 0%, #00FF94 100%) !important;
            box-shadow: 0 0 30px rgba(0, 255, 148, 0.6) !important;
            transform: translateY(-2px) !important;
        }
        
        div.stButton > button:active {
            transform: translateY(0px) !important;
        }
        
        /* ============================================
           NEON SLIDERS
           ============================================ */
        div[data-testid="stSlider"] > div > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
        }
        
        div[data-testid="stSlider"] > div > div > div > div {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%) !important;
            box-shadow: 0 0 10px rgba(0, 255, 148, 0.5) !important;
        }
        
        /* Slider thumb */
        div[data-testid="stSlider"] [role="slider"] {
            background: #00FF94 !important;
            border: 3px solid #0a0e27 !important;
            box-shadow: 0 0 15px rgba(0, 255, 148, 0.8) !important;
        }
        
        /* ============================================
           ROUNDED INPUT BOXES
           ============================================ */
        input, textarea, select, 
        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="textarea"] {
            border-radius: 15px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            padding: 12px !important;
        }
        
        /* Streamlit selectbox specific styling */
        div[data-baseweb="select"] > div {
            border-radius: 15px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Selectbox dropdown arrow container */
        div[data-baseweb="select"] > div > div {
            background: transparent !important;
            border-radius: 15px !important;
        }
        
        /* Text inside selectbox */
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] div[role="button"] {
            color: #ffffff !important;
            background: transparent !important;
            border: none !important;
        }
        
        /* Number input styling */
        div[data-testid="stNumberInput"] input {
            border-radius: 15px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
        }
        
        /* File uploader styling */
        div[data-testid="stFileUploader"] {
            border-radius: 15px !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        input:focus, textarea:focus, select:focus,
        div[data-baseweb="select"]:focus-within {
            border: 1px solid #00FF94 !important;
            box-shadow: 0 0 15px rgba(0, 255, 148, 0.3) !important;
            outline: none !important;
        }
        
        /* ============================================
           TABS WITH NEON STYLE
           ============================================ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: transparent !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: rgba(255, 255, 255, 0.7) !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #00FF94 !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%) !important;
            border: none !important;
            color: #0a0e27 !important;
            box-shadow: 0 0 20px rgba(0, 255, 148, 0.4) !important;
        }
        
        /* ============================================
           DATAFRAME TABLES
           ============================================ */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            overflow: hidden !important;
        }
        
        /* ============================================
           SIDEBAR STYLING
           ============================================ */
        section[data-testid="stSidebar"] {
            background: rgba(10, 14, 39, 0.95) !important;
            backdrop-filter: blur(10px) !important;
            border-right: 1px solid rgba(0, 255, 148, 0.2) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }
        
        /* ============================================
           PLOTLY CHARTS
           ============================================ */
        div[data-testid="stPlotlyChart"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 15px !important;
        }
        
        /* ============================================
           TEXT ELEMENTS
           ============================================ */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(0, 255, 148, 0.3) !important;
        }
        
        h1 {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        p, label, span {
            color: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* ============================================
           SCROLLBAR STYLING
           ============================================ */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #00E5FF 0%, #00FF94 100%);
        }
        
        /* ============================================
           EXPANDER STYLING
           ============================================ */
        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        div[data-testid="stExpander"] summary {
            color: #00FF94 !important;
            font-weight: 600 !important;
        }
        
        /* ============================================
           ALERT/INFO BOXES
           ============================================ */
        div[data-testid="stAlert"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            border-left: 4px solid #00FF94 !important;
        }
        
        /* ============================================
           PROGRESS BAR
           ============================================ */
        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%) !important;
            box-shadow: 0 0 15px rgba(0, 255, 148, 0.5) !important;
        }
        </style>
    """
