import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from src.loader import load_all_salaries
from src.logic import calculate_taxes, project_savings, calculate_thriving_score, format_currency
from src.styles.custom_css import get_custom_css
from src.viz_factory import load_lottie_url, get_lottie_animations

# --- CACHED MAP DATA PROCESSING ---
@st.cache_data
def prepare_map_data(filtered_df, selected_category):
    """Cache map data processing to prevent reloading on every rerun."""
    map_data = filtered_df.copy()
    # Normalize salary for bubble size
    map_data['Salary_Normalized'] = (map_data['Salary'] / map_data['Salary'].min()) * 50
    
    # Create professional hover template
    map_data['hover_text'] = map_data.apply(
        lambda row: (
            f"<b>{row['City']}, {row['State']}</b><br>"
            f"<b>Annual Salary:</b> ${row['Salary']:,.0f}<br>"
            f"<b>Monthly Rent:</b> ${row['Rent']:,.0f}<br>"
            f"<b>Cost of Living Index:</b> {row['COL']}<br>"
            f"<b>Thriving Score:</b> {int(row['Thriving_Score'])}/100<br>"
            f"━━━━━━━━━━━━━━━━<br>"
            f"<b>Rating:</b> {'Excellent' if row['Thriving_Score'] >= 80 else 'Very Good' if row['Thriving_Score'] >= 70 else 'Good' if row['Thriving_Score'] >= 60 else 'Fair' if row['Thriving_Score'] >= 50 else 'Challenging'}"
        ),
        axis=1
    )
    return map_data

# Load environment variables from .env file
load_dotenv()

# --- PAGE SETUP ---
st.set_page_config(page_title="NextStep", page_icon="🎓", layout="wide")

# --- LOAD DATA ---
try:
    df = load_all_salaries()
    if df.empty:
        st.error("⚠️ No data loaded. Please check your data source.")
        st.stop()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# --- APPLY CUSTOM CYBERPUNK/PREMIUM THEME ---
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- LOAD LOTTIE ANIMATIONS (cached) ---
if 'lottie_loaded' not in st.session_state:
    lottie_animations = get_lottie_animations()
    st.session_state['robot_animation'] = load_lottie_url(lottie_animations['ai_brain'])
    st.session_state['lottie_loaded'] = True

# --- INITIALIZE SESSION STATE ---
if 'onboarding_complete' not in st.session_state:
    st.session_state['onboarding_complete'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'selected_category' not in st.session_state:
    st.session_state['selected_category'] = None
if 'debt' not in st.session_state:
    st.session_state['debt'] = 30000
if 'lifestyle' not in st.session_state:
    st.session_state['lifestyle'] = "Balanced"
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'ai_results' not in st.session_state:
    st.session_state['ai_results'] = None

# ======================================
# ONBOARDING SCREEN
# ======================================
if not st.session_state['onboarding_complete']:
    # Hide sidebar during onboarding
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center; color: #00FF94; font-size: 48px; margin-bottom: 10px;'>🎓 NextStep</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 18px; margin-bottom: 40px;'>Plan your life after the cap and gown.</p>", unsafe_allow_html=True)

        with st.form("onboarding_form"):
            st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
            user_name = st.text_input("👤 Enter Your Name", placeholder="John Doe", label_visibility="visible", help=None)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
            available_categories = df['Category'].unique().tolist()
            selected_category = st.selectbox("💼 Select Your Career Path", available_categories, index=None, placeholder="Choose a field...", label_visibility="visible")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
            debt = st.number_input("💰 Student Loan Debt ($)", min_value=0, max_value=500000, value=30000, step=1000, label_visibility="visible")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
            lifestyle = st.select_slider("✨ Lifestyle Preference", options=["Frugal", "Balanced", "Boujee"], value="Balanced", label_visibility="visible")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<h3 style='text-align: center; color: #00FF94; margin-top: 30px; margin-bottom: 15px;'>📄 Upload Your Resume (Optional)</h3>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

            st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("🚀 Begin Your Journey", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if submit_button:
                if not user_name:
                    st.error("Please enter your name to continue.")
                elif not selected_category:
                    st.error("Please select a career path to continue.")
                else:
                    st.session_state['user_name'] = user_name
                    st.session_state['selected_category'] = selected_category
                    st.session_state['debt'] = debt
                    st.session_state['lifestyle'] = lifestyle
                    st.session_state['uploaded_file'] = uploaded_file

                    # Process resume if uploaded
                    if uploaded_file is not None:
                        with st.spinner("🤖 Analyzing your resume..."):
                            try:
                                from src.resume_parser import parse_resume_with_ai
                                api_key = os.getenv('GEMINI_API_KEY')
                                if api_key:
                                    ai_results = parse_resume_with_ai(uploaded_file, api_key)
                                    st.session_state['ai_results'] = ai_results
                                    st.session_state['switch_to_resume_tab'] = True
                                    st.success("✅ Resume analyzed!")
                                else:
                                    st.warning("⚠️ API key not found. Skipping AI analysis.")
                                    st.session_state['ai_results'] = None
                            except Exception as e:
                                st.error(f"❌ Resume analysis failed: {e}")
                                st.session_state['ai_results'] = None

                    # Mark onboarding as complete
                    st.session_state['onboarding_complete'] = True
                    st.session_state['switch_to_resume_tab'] = uploaded_file is not None
                    st.rerun()

    st.stop()  # Stop here if onboarding not complete

# ======================================
# MAIN APP (after onboarding)
# ======================================

# Get user data from session state
user_name = st.session_state.get('user_name', 'User')
selected_category = st.session_state.get('selected_category', df['Category'].unique()[0])
debt = st.session_state.get('debt', 30000)
lifestyle = st.session_state.get('lifestyle', 'Balanced')
uploaded_file = st.session_state.get('uploaded_file', None)

# --- SIDEBAR: USER INFO & CONTROLS ---
available_categories = df['Category'].unique().tolist()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("NextStep")

    st.markdown(f"### Welcome, {user_name}! 👋")

    st.divider()
    st.markdown("#### Update Your Settings")
    selected_category = st.selectbox(
        "Career Path",
        available_categories,
        index=list(available_categories).index(selected_category) if selected_category in available_categories else 0,
        key="main_category"
    )
    debt = st.number_input("Student Loan Debt ($)", min_value=0, max_value=500000, value=debt, step=1000, key="main_debt")
    lifestyle = st.select_slider("Lifestyle Preference", options=["Frugal", "Balanced", "Boujee"], value=lifestyle, key="main_lifestyle")

    st.divider()
    st.markdown("#### 📄 Upload Resume")

    # Show robot animation
    if st.session_state.get('robot_animation'):
        st_lottie(st.session_state['robot_animation'], height=120, key="sidebar_robot")

    new_uploaded_file = st.file_uploader("Upload a new resume", type="pdf", label_visibility="collapsed", key="main_resume")

    if new_uploaded_file is not None and new_uploaded_file != uploaded_file:
        with st.spinner("🤖 Analyzing new resume..."):
            try:
                from src.resume_parser import parse_resume_with_ai

                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    ai_results = parse_resume_with_ai(new_uploaded_file, api_key)
                    st.session_state['ai_results'] = ai_results
                    st.session_state['uploaded_file'] = new_uploaded_file
                    st.success("✅ Resume analyzed!")
                    st.session_state['switch_to_resume_tab'] = True
                    st.rerun()
                else:
                    st.warning("⚠️ API key not found.")
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

    # Update session state when values change
    if selected_category != st.session_state.get('selected_category'):
        st.session_state['selected_category'] = selected_category
        st.rerun()
    if debt != st.session_state.get('debt'):
        st.session_state['debt'] = debt
        st.rerun()
    if lifestyle != st.session_state.get('lifestyle'):
        st.session_state['lifestyle'] = lifestyle
        st.rerun()

# --- FILTER DATA BASED ON SELECTION ---
filtered_data = df[df['Category'] == selected_category].copy()

# Check if filtered data is empty
if filtered_data.empty:
    st.error(f"⚠️ No data found for {selected_category}. Please select a different career path.")
    st.stop()

# --- DYNAMIC METRICS CALCULATION ---
# Calculate Thriving Score for each city based on user's debt and lifestyle
filtered_data['Thriving_Score'] = filtered_data.apply(
    lambda row: calculate_thriving_score(
        calculate_taxes(row['Salary'], row['State']) - ((debt / 10000) * 115 if debt > 0 else 0),
        row['Rent'],
        row['COL']
    ),
    axis=1
)

# Find the city with BEST thriving score (not just highest salary)
top_city_row = filtered_data.loc[filtered_data['Thriving_Score'].idxmax()]
top_city = top_city_row['City']
top_score = top_city_row['Thriving_Score']
avg_salary = filtered_data['Salary'].mean()

# For display purposes
data_for_display = filtered_data

# --- KEY METRICS ROW (POST-GAME STATS SCREEN) ---
# Calculate real savings for the top recommended city
top_city_net = calculate_taxes(top_city_row['Salary'], top_city_row['State'])
top_city_savings = project_savings(top_city_net, top_city_row['Rent'], top_city_row['COL'], lifestyle)
top_city_savings -= ((debt / 10000) * 115 if debt > 0 else 0)  # Subtract loan payment

col1, col2, col3 = st.columns(3)
col1.metric("🎯 Best City for You", top_city, f"Score: {top_score}/100")

# Wealth Velocity with progress bar in col2
with col2:
    st.metric("💰 Wealth Velocity", f"${top_city_savings:,.0f}/mo", f"in {top_city}")
    # Progress bar for Financial Freedom based on savings (cap at $5,000)
    if top_city_savings > 0:
        progress_value = min(top_city_savings / 5000, 1.0)
        st.progress(progress_value, text="Financial Freedom Progress")
    else:
        st.progress(0, text="Financial Freedom Progress")

col3.metric("💼 Average Salary", f"${avg_salary:,.0f}", "For this role")

st.divider()

# --- TABBED INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["Map View", "Budget Lab", "Resume Pivot", "🎤 Simulate Interview"])

# If AI just finished, inject JS to click the Resume Pivot tab
if st.session_state.get('switch_to_resume_tab', False):
    st.session_state['switch_to_resume_tab'] = False
    components.html("""
        <script>
            const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
            if (tabs.length >= 3) { tabs[2].click(); }
        </script>
    """, height=0)
    st.toast('🤖 AI Analysis Complete! Results are in the Resume Pivot tab.', icon='✅')

# Auto-switch to interview tab if flagged
if st.session_state.get('switch_to_interview_tab', False):
    st.session_state['switch_to_interview_tab'] = False
    components.html("""
        <script>
            const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
            if (tabs.length >= 4) { tabs[3].click(); }
        </script>
    """, height=0)

# ========== TAB 1: MAP VIEW ==========
with tab1:
    st.subheader(f"Where can a {selected_category} thrive?")

    # Get top city from filtered data
    top_row = filtered_data.loc[filtered_data['Salary'].idxmax()]
    spotlight_city = top_row['City']
    spotlight_salary = f"${top_row['Salary']:,.0f}"
    spotlight_text = f"Highest salary for {selected_category}: **{spotlight_salary}/year**"

    # Create a 'Spotlight' section for the #1 city
    with st.container():
        st.markdown("### 🌟 Your Best Move")
        inner_col1, inner_col2 = st.columns([1, 2])
        with inner_col1:
            st.image("https://img.icons8.com/fluency/96/star.png")
        with inner_col2:
            st.subheader(spotlight_city)
            st.write(spotlight_text)

    st.divider()

    # Use cached map data processing for better performance
    map_data = prepare_map_data(filtered_data, selected_category)

    # Initialize map state for preserving zoom/center
    if 'map_zoom' not in st.session_state:
        st.session_state['map_zoom'] = 3
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = {"lat": 37.0902, "lon": -95.7129}

    fig_map = px.scatter_mapbox(
        map_data,
        lat="Lat",
        lon="Lon",
        size="Salary_Normalized",
        color="Thriving_Score",
        hover_name="City",
        color_continuous_scale="RdYlGn",
        size_max=45,
        zoom=st.session_state['map_zoom'],
        center=st.session_state['map_center'],
        mapbox_style="carto-darkmatter",
        title=f"<b>{selected_category}</b> Opportunities Across the US",
        custom_data=['hover_text']
    )

    # Update hover template
    fig_map.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>',
        marker=dict(opacity=0.8)
    )

    # Force consistent dark theme regardless of browser settings
    fig_map.update_layout(
        height=600,
        autosize=True,
        paper_bgcolor='#0a0e27',
        plot_bgcolor='#0a0e27',
        font=dict(color='#00FF94', family='Courier New, monospace', size=14),
        title=dict(
            font=dict(size=20, color='#00FF94', family='Courier New, monospace'),
            x=0.5,
            xanchor='center'
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="VIABILITY<br>SCORE",
                font=dict(color='#00FF94', size=12)
            ),
            tickfont=dict(color='#00FF94'),
            bgcolor='rgba(10, 14, 39, 0.95)',
            bordercolor='#00FF94',
            borderwidth=2,
            len=0.7
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        # Force dark theme settings
        template='plotly_dark',
        mapbox=dict(
            style='carto-darkmatter',
            zoom=st.session_state['map_zoom'],
            center=st.session_state['map_center']
        )
    )

    # Render map with responsive container
    st.plotly_chart(fig_map, use_container_width=True, config={
        'displayModeBar': True,
        'scrollZoom': True,
        'responsive': True
    })

    with st.expander("See the math behind your score"):
        st.write(f"Based on a {lifestyle} lifestyle with ${debt:,} in debt...")
        # Sort by Thriving Score descending so best cities are at top
        sorted_data = filtered_data.sort_values('Thriving_Score', ascending=False)
        st.dataframe(sorted_data)

# ========== TAB 2: BUDGET LAB ==========
with tab2:
    st.subheader("Financial Reality Check")

    # Add city selector for deep dive analysis with toast notification
    target_city = st.selectbox('🎯 Analyze a City', filtered_data['City'].unique())

    # Trigger toast when city changes
    if 'last_selected_city' not in st.session_state:
        st.session_state['last_selected_city'] = target_city

    if st.session_state['last_selected_city'] != target_city:
        st.toast(f'🏙️ Simulation Updated: {target_city} selected', icon='🏙️')
        st.session_state['last_selected_city'] = target_city

    # Get the specific city data
    city_data = filtered_data[filtered_data['City'] == target_city].iloc[0]

    # Extract city-specific values
    city_salary = city_data['Salary']
    city_rent = city_data['Rent']
    city_state = city_data['State']
    city_col = city_data['COL']
    city_thriving_score = city_data['Thriving_Score']

    # Calculate real financial metrics using logic functions
    monthly_net = calculate_taxes(city_salary, city_state)

    # Estimate monthly loan payment (10-year standard repayment)
    monthly_loan_payment = (debt / 10000) * 115 if debt > 0 else 0

    # Calculate projected savings using corrected function call
    monthly_savings = project_savings(monthly_net, city_rent, city_col, lifestyle)

    # Calculate taxes paid (for donut chart)
    gross_monthly = city_salary / 12
    taxes_paid = gross_monthly - monthly_net

    # Estimate lifestyle costs based on user's preference
    lifestyle_costs = {
        'Frugal': 900,
        'Balanced': 1700,
        'Boujee': 3000
    }
    lifestyle_cost = lifestyle_costs.get(lifestyle, 1700)

    # Centered Pie Chart Layout
    st.markdown("### Monthly Budget Breakdown")
    
    _, chart_col, _ = st.columns([1, 2, 1])
    
    with chart_col:
        # Real budget data based on calculations
        budget_data = {
            'Category': ['Rent', 'Taxes', 'Loans', 'Lifestyle', 'Savings'],
            'Amount': [
                city_rent,
                taxes_paid,
                monthly_loan_payment,
                lifestyle_cost,
                max(0, monthly_savings)  # Show 0 if negative
            ]
        }
        df_budget = pd.DataFrame(budget_data)

        fig_donut = go.Figure(data=[go.Pie(
            labels=df_budget['Category'],
            values=df_budget['Amount'],
            hole=0.5,
            marker=dict(
                colors=['#FF4B4B', '#FFA500', '#FFD700', '#9D4EDD', '#00D9FF'],
                line=dict(color='#0E1117', width=2)
            ),
            textfont=dict(size=16, color='white')
        )])

        fig_donut.update_layout(
            showlegend=True,
            height=400,
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117',
            font=dict(color='white', size=14),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    # Dynamic insight sentence (centered)
    if monthly_savings > 0:
        st.success(f"💰 In **{target_city}**, your Wealth Velocity is **${monthly_savings:,.2f}/mo** - Building your empire!")
    else:
        st.error(f"⚠️ In **{target_city}**, Burn Rate exceeds income by **${abs(monthly_savings):,.2f}/mo** with {lifestyle} lifestyle.")

    st.divider()

    # Financial Stats Section
    st.markdown("### 📊 Post-Game Financial Stats")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("💵 Net Income", f"${monthly_net:,.0f}/mo", "After taxes")
    with col_b:
        st.metric("🔥 Burn Rate", f"${city_rent:,.0f}/mo", "Housing cost")
    with col_c:
        st.metric("💰 Wealth Velocity", f"${monthly_savings:,.0f}/mo",
                  "💰" if monthly_savings > 1000 else ("⚠️" if monthly_savings < 0 else "📊"))
    with col_d:
        st.metric("📈 Annual Projection", f"${monthly_savings * 12:,.0f}/yr", "If consistent")



# ========== TAB 3: RESUME PIVOT ==========
with tab3:
    st.subheader("Resume Analysis & Career Pivot")

    # Show AI results banner if available
    if st.session_state.get('ai_results'):
        st.markdown("""
            <div style='background: linear-gradient(135deg, #00FF94 0%, #00E5FF 100%); 
                        padding: 25px; border-radius: 15px; margin-bottom: 25px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
                <h2 style='color: #0a0e27; margin: 0; text-align: center;'>🎉 Your AI Resume Analysis is Ready!</h2>
                <p style='color: #0a0e27; margin: 10px 0 0 0; text-align: center; font-weight: 600;'>Scroll down to see detailed insights</p>
            </div>
        """, unsafe_allow_html=True)

    # --- DISPLAY AI RESULTS IF AVAILABLE ---
    if st.session_state.get('ai_results'):
        ai_data = st.session_state['ai_results']

        # Prominent AI Analysis Results Card
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 25px; border-radius: 12px; margin-bottom: 20px;'>
                <h2 style='color: white; margin: 0;'>🤖 AI-Powered Resume Analysis</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 5px 0;'>Deep analysis powered by Gemini AI</p>
            </div>
        """, unsafe_allow_html=True)

        # Display key AI insights
        if 'tech_skills' in ai_data and ai_data['tech_skills']:
            st.markdown("### 🎯 Skills Identified by AI")
            skills_text = ", ".join(ai_data['tech_skills'][:10])  # Show top 10
            st.success(f"**Detected Skills:** {skills_text}")

        if 'career_summary' in ai_data:
            st.markdown("### 💼 Career Summary")
            st.info(ai_data['career_summary'])

        if 'recommended_roles' in ai_data:
            st.markdown("### 💡 Recommended Roles for You")
            for rec in ai_data['recommended_roles'][:5]:  # Show top 5
                st.write(f"• {rec}")

        st.divider()

    # Hardcoded dictionary of hot keywords for STEM careers
    STEM_KEYWORDS = {
        'Data Scientist': ['Python', 'SQL', 'TensorFlow', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-learn', 'Statistics', 'A/B Testing', 'PyTorch'],
        'Cybersecurity Analyst': ['Firewalls', 'Penetration Testing', 'Security', 'SIEM', 'Risk Assessment', 'Encryption', 'Network Security', 'Incident Response', 'Compliance', 'Threat Analysis'],
        'Software Engineer': ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Git', 'API', 'AWS', 'Docker', 'Agile'],
        'Machine Learning Engineer': ['Python', 'TensorFlow', 'PyTorch', 'Deep Learning', 'Neural Networks', 'MLOps', 'Kubernetes', 'Model Deployment', 'Computer Vision', 'NLP'],
        'Cloud Architect': ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker', 'Terraform', 'CI/CD', 'Microservices', 'Cloud Security', 'DevOps'],
        'Data Engineer': ['Python', 'SQL', 'Spark', 'Hadoop', 'ETL', 'Data Pipeline', 'Airflow', 'Kafka', 'Snowflake', 'BigQuery'],
        'DevOps Engineer': ['Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'Linux', 'Terraform', 'Ansible', 'Git', 'AWS', 'Monitoring'],
        'UX Designer': ['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research', 'Wireframing', 'UI Design', 'Design Systems', 'Usability Testing', 'InVision'],
        'Product Manager': ['Product Strategy', 'Roadmap', 'Agile', 'SQL', 'A/B Testing', 'User Stories', 'Analytics', 'Stakeholder Management', 'Product Vision', 'Market Research']
    }

    # Get relevant keywords for selected career
    relevant_keywords = STEM_KEYWORDS.get(selected_category, ['Python', 'SQL', 'Git', 'Communication', 'Problem Solving'])

    if uploaded_file is not None:
        st.success(f"✅ Resume uploaded: **{uploaded_file.name}**")

        # Try to extract text from PDF
        resume_text = ""
        try:
            # Attempt to use pypdf if available
            import pypdf
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text().upper()
        except ImportError:
            # Fallback: Mock resume text for demo if pypdf not installed
            st.info("📝 Using demo analysis mode (install pypdf for real PDF parsing)")
            resume_text = """
            EXPERIENCED SOFTWARE ENGINEER WITH PYTHON, JAVASCRIPT, AND REACT EXPERIENCE.
            WORKED WITH AWS, DOCKER, AND GIT IN PRODUCTION ENVIRONMENTS.
            STRONG BACKGROUND IN MACHINE LEARNING AND DATA ANALYSIS.
            PROFICIENT IN SQL AND DATABASE DESIGN.
            """.upper()
        except Exception as e:
            st.warning(f"Could not parse PDF: {e}. Using demo mode.")
            resume_text = "PYTHON SQL AWS DOCKER GIT".upper()

        st.divider()

        # Keyword Analysis Section
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 🎯 Keywords Found")
            st.caption("Skills detected in your resume")

            found_keywords = []
            for keyword in relevant_keywords:
                if keyword.upper() in resume_text:
                    found_keywords.append(keyword)
                    st.markdown(f"<div style='background-color: #1a4d2e; padding: 8px; margin: 4px 0; border-radius: 5px; border-left: 4px solid #00ff88;'>✅ <b>{keyword}</b> detected</div>", unsafe_allow_html=True)

            if not found_keywords:
                st.warning("No keywords detected. Make sure your resume includes technical skills!")

        with col_right:
            st.markdown("### 📈 Skills to Add")
            st.caption("Boost your resume with these")

            missing_keywords = []
            for keyword in relevant_keywords:
                if keyword.upper() not in resume_text:
                    missing_keywords.append(keyword)
                    st.markdown(f"<div style='background-color: #4d1a1a; padding: 8px; margin: 4px 0; border-radius: 5px; border-left: 4px solid #ff4444;'>❌ <b>{keyword}</b> - Recommended</div>", unsafe_allow_html=True)

            if not missing_keywords:
                st.success("🎉 You have all the key skills!")

        st.divider()

        # Analysis Summary
        st.markdown("### 📊 Analysis Summary")
        match_percentage = (len(found_keywords) / len(relevant_keywords)) * 100 if relevant_keywords else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Keywords Found", f"{len(found_keywords)}/{len(relevant_keywords)}", f"{match_percentage:.0f}% match")
        col2.metric("Skills Gap", len(missing_keywords), "to learn")
        col3.metric("Career Fit", "Strong" if match_percentage > 60 else ("Medium" if match_percentage > 30 else "Growing"),
                    "🎯" if match_percentage > 60 else "📈")

        # Progress bar
        st.progress(match_percentage / 100)
        st.caption(f"Your resume matches {match_percentage:.0f}% of key skills for {selected_category} roles")

        # Action items
        if missing_keywords:
            with st.expander("💡 Action Plan to Close the Gap"):
                st.markdown("**Recommended next steps:**")
                for i, keyword in enumerate(missing_keywords[:5], 1):  # Show top 5
                    st.write(f"{i}. Learn **{keyword}** - Add to resume once proficient")
                st.write("\n**Resources:**")
                st.write("- Online courses: Coursera, Udemy, freeCodeCamp")
                st.write("- Practice projects: GitHub, Kaggle, personal portfolio")
                st.write("- Certifications: AWS, Google Cloud, CompTIA")

    else:
        # No file uploaded - show prompt
        st.warning("📄 Upload your resume in the sidebar to get an instant keyword analysis!")

        st.markdown("---")

        # Preview of what they'll get
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🔍 What We Analyze")
            st.write(f"✓ **{len(relevant_keywords)} key skills** for {selected_category}")
            st.write("✓ **ATS-friendly keywords** (what recruiters search for)")
            st.write("✓ **Skills gap analysis** to prioritize learning")
            st.write("✓ **Career fit score** for your target role")

        with col_b:
            st.markdown("#### 🎯 Hot Keywords for Your Role")
            st.caption(f"Top skills for {selected_category}:")
            for keyword in relevant_keywords[:6]:  # Show first 6
                st.markdown(f"<div style='background-color: #1E2130; padding: 6px 12px; margin: 4px 0; border-radius: 5px; display: inline-block;'>🔹 {keyword}</div>", unsafe_allow_html=True)

# ========== TAB 4: SIMULATE INTERVIEW ==========
with tab4:
    st.subheader("🎤 AI Mock Interview Practice")
    
    # Interview mode selector
    if 'voice_interview_mode' not in st.session_state:
        st.session_state['voice_interview_mode'] = 'setup'  # setup, active, report
    
    if st.session_state['voice_interview_mode'] == 'setup':
        st.markdown("""
            <div style='background: linear-gradient(135deg, #9D4EDD 0%, #00D9FF 100%); 
                        padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                <h3 style='color: white; margin: 0;'>🎥 Voice + Video Interview</h3>
                <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>
                    Real-time AI interview with camera and microphone
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_setup, col_info = st.columns([2, 1])
        
        with col_setup:
            st.markdown("### 📋 Interview Setup")
            st.info(f"**Target Role:** {selected_category}")
            st.caption(f"**Candidate:** {user_name}")
            
            st.markdown("#### ⚠️ Before Starting:")
            st.markdown("""
            1. **Allow camera & microphone** when prompted
            2. **Speak clearly** into your microphone
            3. Interview ends after **5 questions**
            4. You'll receive a **70/30 scored report**
            """)
        
        with col_info:
            st.markdown("### 📊 Scoring System")
            st.markdown("""
            <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;'>
                <p><strong style='color: #00FF94;'>70%</strong> Content Quality</p>
                <p style='font-size: 12px; opacity: 0.7;'>Logic, relevance, depth of answers</p>
                <p style='margin-top: 10px;'><strong style='color: #00D9FF;'>30%</strong> Behavioral</p>
                <p style='font-size: 12px; opacity: 0.7;'>Eye contact, confidence, body language</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Check if server is needed
        st.warning("📢 **Make sure the interview server is running:** `uvicorn src.interview.server:app --reload --port 8000`")
        
        if st.button("🚀 Start Voice Interview", type="primary", use_container_width=True):
            st.session_state['voice_interview_mode'] = 'active'
            st.rerun()
    
    elif st.session_state['voice_interview_mode'] == 'active':
        # Full embedded interview component with camera, mic, and WebSocket
        interview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Inter', -apple-system, sans-serif; 
                    background: transparent;
                    color: white;
                }}
                .interview-container {{
                    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                    border-radius: 16px;
                    padding: 24px;
                    min-height: 700px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .status {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 16px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    font-size: 14px;
                }}
                .status-dot {{
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    animation: pulse 1.5s infinite;
                }}
                .status-dot.connecting {{ background: #FFD700; }}
                .status-dot.active {{ background: #00FF94; }}
                .status-dot.processing {{ background: #00D9FF; animation: pulse 0.5s infinite; }}
                .status-dot.error {{ background: #FF4B4B; }}
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                }}
                .main-content {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                .video-section {{
                    background: #000;
                    border-radius: 12px;
                    overflow: hidden;
                    position: relative;
                    aspect-ratio: 4/3;
                }}
                #localVideo {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transform: scaleX(-1);
                }}
                .video-overlay {{
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    background: rgba(0,0,0,0.7);
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }}
                .chat-section {{
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }}
                .question-box {{
                    background: rgba(0, 255, 148, 0.1);
                    border-left: 4px solid #00FF94;
                    padding: 20px;
                    border-radius: 0 12px 12px 0;
                    min-height: 120px;
                }}
                .question-label {{
                    opacity: 0.7;
                    font-size: 14px;
                    margin-bottom: 8px;
                }}
                .question-text {{
                    font-size: 18px;
                    line-height: 1.5;
                }}
                .transcript-box {{
                    background: rgba(255,255,255,0.05);
                    border-radius: 12px;
                    padding: 16px;
                    flex: 1;
                    min-height: 150px;
                    max-height: 200px;
                    overflow-y: auto;
                }}
                .transcript-label {{
                    opacity: 0.7;
                    font-size: 14px;
                    margin-bottom: 8px;
                }}
                .controls {{
                    display: flex;
                    gap: 12px;
                    margin-top: 20px;
                }}
                .btn {{
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 0.2s;
                }}
                .btn-primary {{
                    background: linear-gradient(135deg, #00FF94 0%, #00D9FF 100%);
                    color: #0a0e27;
                    font-weight: 600;
                }}
                .btn-danger {{
                    background: #FF4B4B;
                    color: white;
                }}
                .btn:hover {{ transform: scale(1.02); }}
                .btn:disabled {{
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }}
                .audio-level {{
                    height: 6px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 3px;
                    margin-top: 12px;
                    overflow: hidden;
                }}
                .audio-level-bar {{
                    height: 100%;
                    background: linear-gradient(90deg, #00FF94, #00D9FF);
                    width: 0%;
                    transition: width 0.1s;
                }}
                .progress-bar {{
                    height: 4px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 2px;
                    margin-bottom: 20px;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #9D4EDD, #00D9FF);
                    border-radius: 2px;
                    transition: width 0.3s;
                }}
                .error-message {{
                    background: rgba(255,75,75,0.2);
                    border: 1px solid #FF4B4B;
                    padding: 12px;
                    border-radius: 8px;
                    margin-top: 12px;
                }}
                .permission-prompt {{
                    text-align: center;
                    padding: 40px;
                }}
                .permission-prompt h3 {{
                    margin-bottom: 16px;
                }}
            </style>
        </head>
        <body>
            <div class="interview-container">
                <div class="header">
                    <h2>🎤 Mock Interview: {selected_category}</h2>
                    <div class="status">
                        <div class="status-dot connecting" id="statusDot"></div>
                        <span id="statusText">Connecting...</span>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                
                <div id="permissionPrompt" class="permission-prompt">
                    <h3>📷 Camera & Microphone Access Required</h3>
                    <p style="opacity: 0.7; margin-bottom: 20px;">Click Start to allow access and begin your interview</p>
                    <button class="btn btn-primary" onclick="initializeMedia()">
                        🚀 Start Interview
                    </button>
                </div>
                
                <div id="mainContent" class="main-content" style="display: none;">
                    <div class="video-section">
                        <video id="localVideo" autoplay muted playsinline></video>
                        <div class="video-overlay">
                            <span id="turnIndicator">🎤 Listening...</span>
                        </div>
                    </div>
                    
                    <div class="chat-section">
                        <div class="question-box">
                            <div class="question-label">🤖 Interviewer:</div>
                            <div class="question-text" id="currentQuestion">Waiting for first question...</div>
                        </div>
                        
                        <div class="transcript-box">
                            <div class="transcript-label">📝 Your Response:</div>
                            <div id="transcript">Start speaking when ready...</div>
                        </div>
                        
                        <div class="audio-level">
                            <div class="audio-level-bar" id="audioLevel"></div>
                        </div>
                        
                        <div class="controls">
                            <button class="btn btn-primary" id="submitBtn" onclick="submitAnswer()" disabled>
                                ✅ Submit Answer
                            </button>
                            <button class="btn btn-danger" onclick="endInterview()">
                                🛑 End Interview
                            </button>
                        </div>
                    </div>
                </div>
                
                <div id="errorBox" class="error-message" style="display: none;"></div>
            </div>
            
            <script>
                const WS_URL = 'ws://localhost:8000/ws/interview/';
                const TARGET_ROLE = '{selected_category}';
                const USER_NAME = '{user_name}';
                
                let ws = null;
                let sessionId = null;
                let mediaStream = null;
                let recognition = null;
                let transcript = '';
                let turnNumber = 0;
                let totalTurns = 5;
                let audioContext = null;
                let analyser = null;
                let videoFrames = [];
                let frameInterval = null;
                
                function updateStatus(status, color) {{
                    document.getElementById('statusDot').className = 'status-dot ' + color;
                    document.getElementById('statusText').textContent = status;
                }}
                
                function showError(message) {{
                    const errorBox = document.getElementById('errorBox');
                    errorBox.style.display = 'block';
                    errorBox.textContent = '❌ ' + message;
                }}
                
                async function initializeMedia() {{
                    try {{
                        updateStatus('Requesting permissions...', 'connecting');
                        
                        // Request camera and microphone
                        mediaStream = await navigator.mediaDevices.getUserMedia({{
                            video: {{ width: 640, height: 480, facingMode: 'user' }},
                            audio: {{ sampleRate: 16000, channelCount: 1 }}
                        }});
                        
                        // Show video
                        const video = document.getElementById('localVideo');
                        video.srcObject = mediaStream;
                        
                        // Hide permission prompt, show main content
                        document.getElementById('permissionPrompt').style.display = 'none';
                        document.getElementById('mainContent').style.display = 'grid';
                        
                        // Setup audio level visualization
                        setupAudioVisualization();
                        
                        // Setup speech recognition
                        setupSpeechRecognition();
                        
                        // Start frame capture (1 FPS for behavioral analysis)
                        startFrameCapture();
                        
                        // Create session and connect WebSocket
                        await createSession();
                        
                    }} catch (error) {{
                        console.error('Media error:', error);
                        showError('Failed to access camera/microphone: ' + error.message);
                        updateStatus('Permission denied', 'error');
                    }}
                }}
                
                function setupAudioVisualization() {{
                    audioContext = new AudioContext();
                    const source = audioContext.createMediaStreamSource(mediaStream);
                    analyser = audioContext.createAnalyser();
                    analyser.fftSize = 256;
                    source.connect(analyser);
                    
                    const dataArray = new Uint8Array(analyser.frequencyBinCount);
                    
                    function updateLevel() {{
                        analyser.getByteFrequencyData(dataArray);
                        const avg = dataArray.reduce((a, b) => a + b) / dataArray.length;
                        const level = Math.min(100, avg * 1.5);
                        document.getElementById('audioLevel').style.width = level + '%';
                        requestAnimationFrame(updateLevel);
                    }}
                    updateLevel();
                }}
                
                function setupSpeechRecognition() {{
                    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                        showError('Speech recognition not supported. Please use Chrome.');
                        return;
                    }}
                    
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';
                    
                    recognition.onresult = (event) => {{
                        let interimTranscript = '';
                        let finalTranscript = '';
                        
                        for (let i = event.resultIndex; i < event.results.length; i++) {{
                            if (event.results[i].isFinal) {{
                                finalTranscript += event.results[i][0].transcript + ' ';
                            }} else {{
                                interimTranscript += event.results[i][0].transcript;
                            }}
                        }}
                        
                        transcript += finalTranscript;
                        document.getElementById('transcript').textContent = transcript + interimTranscript;
                        document.getElementById('submitBtn').disabled = transcript.trim().length < 10;
                    }};
                    
                    recognition.onerror = (event) => {{
                        console.error('Speech error:', event.error);
                        if (event.error !== 'no-speech') {{
                            showError('Speech recognition error: ' + event.error);
                        }}
                    }};
                    
                    recognition.onend = () => {{
                        // Restart recognition if interview is still active
                        if (ws && ws.readyState === WebSocket.OPEN) {{
                            try {{ recognition.start(); }} catch(e) {{}}
                        }}
                    }};
                }}
                
                function startFrameCapture() {{
                    const video = document.getElementById('localVideo');
                    const canvas = document.createElement('canvas');
                    canvas.width = 320;
                    canvas.height = 240;
                    const ctx = canvas.getContext('2d');
                    
                    frameInterval = setInterval(() => {{
                        ctx.drawImage(video, 0, 0, 320, 240);
                        const frame = canvas.toDataURL('image/jpeg', 0.5).split(',')[1];
                        videoFrames.push(frame);
                        // Keep only last 10 frames
                        if (videoFrames.length > 10) videoFrames.shift();
                    }}, 1000);
                }}
                
                async function createSession() {{
                    try {{
                        updateStatus('Creating session...', 'connecting');
                        
                        const response = await fetch('http://localhost:8000/session/create', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                target_role: TARGET_ROLE,
                                user_name: USER_NAME
                            }})
                        }});
                        
                        if (!response.ok) {{
                            throw new Error('Server returned ' + response.status);
                        }}
                        
                        const data = await response.json();
                        sessionId = data.session_id;
                        
                        // Connect WebSocket
                        connectWebSocket();
                        
                    }} catch (error) {{
                        console.error('Session error:', error);
                        showError('Failed to connect to server. Is it running on port 8000?');
                        updateStatus('Connection failed', 'error');
                    }}
                }}
                
                function connectWebSocket() {{
                    ws = new WebSocket(WS_URL + sessionId);
                    
                    ws.onopen = () => {{
                        updateStatus('Connected', 'active');
                        // Start interview
                        ws.send(JSON.stringify({{ type: 'start' }}));
                        // Start speech recognition
                        try {{ recognition.start(); }} catch(e) {{}}
                    }};
                    
                    ws.onmessage = (event) => {{
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'question') {{
                            document.getElementById('currentQuestion').textContent = data.text;
                            turnNumber = data.turn_number || turnNumber + 1;
                            document.getElementById('progressFill').style.width = ((turnNumber / totalTurns) * 100) + '%';
                            document.getElementById('turnIndicator').textContent = '🎤 Question ' + turnNumber + '/' + totalTurns;
                            updateStatus('Listening...', 'active');
                            
                            // Clear transcript for new question
                            transcript = '';
                            document.getElementById('transcript').textContent = 'Start speaking...';
                            document.getElementById('submitBtn').disabled = true;
                            
                            if (data.is_final) {{
                                // Interview complete
                                updateStatus('Interview complete!', 'processing');
                            }}
                        }}
                        
                        if (data.type === 'report') {{
                            // Store report and signal completion
                            window.interviewReport = data.data;
                            updateStatus('Report ready!', 'active');
                            document.getElementById('currentQuestion').textContent = '✅ Interview Complete! Close this window to see your report.';
                            document.getElementById('submitBtn').style.display = 'none';
                            
                            // Send message to parent
                            window.parent.postMessage({{
                                type: 'interview_complete',
                                report: data.data
                            }}, '*');
                        }}
                        
                        if (data.type === 'error') {{
                            showError(data.message);
                        }}
                    }};
                    
                    ws.onerror = (error) => {{
                        console.error('WebSocket error:', error);
                        showError('WebSocket connection error');
                        updateStatus('Error', 'error');
                    }};
                    
                    ws.onclose = () => {{
                        updateStatus('Disconnected', 'error');
                        if (recognition) recognition.stop();
                    }};
                }}
                
                function submitAnswer() {{
                    if (!ws || ws.readyState !== WebSocket.OPEN) return;
                    if (transcript.trim().length < 10) return;
                    
                    updateStatus('Processing...', 'processing');
                    document.getElementById('submitBtn').disabled = true;
                    document.getElementById('turnIndicator').textContent = '⏳ Processing...';
                    
                    ws.send(JSON.stringify({{
                        type: 'turn',
                        transcript: transcript,
                        video_frames: videoFrames
                    }}));
                    
                    videoFrames = [];
                }}
                
                function endInterview() {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        ws.send(JSON.stringify({{ type: 'end' }}));
                    }}
                    
                    // Cleanup
                    if (recognition) recognition.stop();
                    if (frameInterval) clearInterval(frameInterval);
                    if (mediaStream) {{
                        mediaStream.getTracks().forEach(track => track.stop());
                    }}
                    
                    window.parent.postMessage({{ type: 'interview_ended' }}, '*');
                }}
            </script>
        </body>
        </html>
        """
        
        # Render the interview component
        components.html(interview_html, height=800, scrolling=False)
        
        # Listen for completion message
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔙 Back to Setup"):
                st.session_state['voice_interview_mode'] = 'setup'
                st.rerun()
        with col2:
            if st.button("📊 View Report (when complete)"):
                st.session_state['voice_interview_mode'] = 'report'
                st.rerun()
    
    elif st.session_state['voice_interview_mode'] == 'report':
        st.markdown("### 📊 Interview Report")
        
        st.info("The report will appear here after you complete the interview. If you just finished, the AI is generating your feedback...")
        
        # Placeholder for report - in production, this would be stored in session state
        # from the WebSocket message
        
        if st.button("🔄 Start New Interview", type="primary"):
            st.session_state['voice_interview_mode'] = 'setup'
            st.rerun()
