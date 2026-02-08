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
tab1, tab2, tab3 = st.tabs(["Map View", "Budget Lab", "Resume Pivot"])

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

# ========== TAB 1: MAP VIEW ==========
with tab1:
    st.subheader(f"Where can a {selected_category} thrive?")

    # Use filtered data (we already checked it's not empty earlier)
    map_data = filtered_data.copy()

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

    # Scatter Mapbox with dark mode
    # Normalize salary for bubble size (make high salaries REALLY pop)
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

    fig_map = px.scatter_mapbox(
        map_data,
        lat="Lat",
        lon="Lon",
        size="Salary_Normalized",
        color="Thriving_Score",
        hover_name="City",
        color_continuous_scale="RdYlGn",
        size_max=45,
        zoom=3,
        center={"lat": 37.0902, "lon": -95.7129},
        mapbox_style="carto-darkmatter",
        title=f"<b>{selected_category}</b> Opportunities Across the US",
        custom_data=['hover_text']
    )

    # Update hover template
    fig_map.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>',
        marker=dict(opacity=0.8)
    )

    fig_map.update_layout(
        height=700,
        paper_bgcolor='rgba(10, 14, 39, 0.95)',
        plot_bgcolor='rgba(10, 14, 39, 0.95)',
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
            bgcolor='rgba(255, 255, 255, 0.05)',
            bordercolor='#00FF94',
            borderwidth=2,
            len=0.7
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)

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

    left_col, right_col = st.columns([1, 1])

    # Left Column: Donut Chart
    with left_col:
        st.markdown("### Monthly Budget Breakdown")

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

        # Dynamic insight sentence
        if monthly_savings > 0:
            st.success(f"💰 In **{target_city}**, your Wealth Velocity is **${monthly_savings:,.2f}/mo** - Building your empire!")
        else:
            st.error(f"⚠️ In **{target_city}**, Burn Rate exceeds income by **${abs(monthly_savings):,.2f}/mo** with {lifestyle} lifestyle.")

    # Right Column: Success Checklist & Updated Metrics (POST-GAME STATS)
    with right_col:
        st.markdown("### 📊 Post-Game Financial Stats")

        # Display key metrics
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("💵 Net Income", f"${monthly_net:,.0f}/mo", "After taxes")
            st.metric("🔥 Burn Rate", f"${city_rent:,.0f}/mo", "Housing cost")
        with col_b:
            st.metric("💰 Wealth Velocity", f"${monthly_savings:,.0f}/mo",
                      "💰" if monthly_savings > 1000 else ("⚠️" if monthly_savings < 0 else "📊"))
            st.metric("📈 Annual Projection", f"${monthly_savings * 12:,.0f}/yr", "If consistent")

        # Progress bar for Wealth Velocity (cap at $5,000)
        st.markdown("#### 🎯 Financial Freedom Progress")
        if monthly_savings > 0:
            wealth_progress = min(monthly_savings / 5000, 1.0)
            st.progress(wealth_progress, text=f"Wealth Building: {int(wealth_progress * 100)}% to Elite Status")
        else:
            st.progress(0, text="Wealth Building: Negative Cash Flow")

        st.divider()

        st.markdown("### 🏆 Achievement Tracker")
        st.markdown("Unlock your financial milestones:")

        st.checkbox("✅ Emergency Fund Built (3-6 months)", value=False)
        st.checkbox("✅ 401k Maxed ($23,000/year)", value=False)
        st.checkbox("✅ High-Interest Debt Paid Off", value=True)
        st.checkbox("✅ Credit Score Above 750", value=True)
        st.checkbox("✅ Side Income Stream Active", value=False)
        st.checkbox("✅ Monthly Budget Tracked", value=True)
        st.checkbox("✅ Investment Portfolio Started", value=False)
        st.checkbox("✅ Health Insurance Secured", value=True)


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
