import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from src.loader import load_all_salaries
from src.logic import calculate_taxes, project_savings, calculate_thriving_score, format_currency

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

# --- CUSTOM STYLING FUNCTION ---
def style_metric_cards():
    """Inject CSS to style metric cards with modern SaaS look"""
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: white; }
        div.stButton > button { background-color: #FF4B4B; color: white; border-radius: 10px; }
        
        /* Metric Card Styling */
        div[data-testid="stMetricValue"] { 
            font-size: 50px; 
        }
        div[data-testid="stMetric"] {
            background-color: #1E2130;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2E3440;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1E2130;
            border-radius: 8px;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF4B4B;
        }
        </style>
        """, unsafe_allow_html=True)

# Apply custom styling
style_metric_cards()

# --- SIDEBAR: USER INPUTS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("NextStep")
    st.write("Plan your life after the cap and gown.")
    
    # Get available categories from data
    available_categories = df['Category'].unique()
    selected_category = st.selectbox("Select your Career Path", available_categories)
    debt = st.number_input("Student Loan Debt ($)", min_value=0, max_value=500000, value=30000, step=1000)
    lifestyle = st.select_slider("Lifestyle Preference", options=["Frugal", "Balanced", "Boujee"])
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if st.button("Calculate Future"):
        st.session_state['selected_category'] = selected_category
        st.session_state['calculate_clicked'] = True
        st.session_state['show_results'] = False  # Will be set to True after AI completes
        
        # If resume is uploaded, trigger AI analysis
        if uploaded_file is not None:
            with st.spinner("🤖 AI is analyzing your resume..."):
                try:
                    from src.resume_parser import parse_resume_with_ai
                    
                    api_key = os.getenv('GEMINI_API_KEY')
                    if not api_key:
                        st.warning("⚠️ API key not found. Resume analysis will be limited.")
                        st.session_state['ai_results'] = None
                    else:
                        # Run AI analysis
                        ai_results = parse_resume_with_ai(uploaded_file, api_key)
                        st.session_state['ai_results'] = ai_results
                        st.session_state['show_results'] = True
                except Exception as e:
                    st.error(f"❌ AI Analysis failed: {e}")
                    st.session_state['ai_results'] = None
        else:
            st.session_state['ai_results'] = None
            st.session_state['show_results'] = True

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

# --- KEY METRICS ROW ---
# Calculate real savings for the top recommended city
top_city_net = calculate_taxes(top_city_row['Salary'], top_city_row['State'])
top_city_savings = project_savings(top_city_net, top_city_row['Rent'], top_city_row['COL'], lifestyle)
top_city_savings -= ((debt / 10000) * 115 if debt > 0 else 0)  # Subtract loan payment

col1, col2, col3 = st.columns(3)
col1.metric("🎯 Best City for You", top_city, f"Score: {top_score}/100")
col2.metric("Your Monthly Savings", f"${top_city_savings:,.0f}", f"in {top_city}")
col3.metric("Average Salary", f"${avg_salary:,.0f}", "For this role")

# --- RESULTS POPUP (if Calculate Future was clicked) ---
if st.session_state.get('show_results', False):
    st.balloons()  # Celebration effect!
    
    # Create a prominent results card
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
            <h2 style='color: white; text-align: center; margin: 0;'>🎉 Your Future is Calculated!</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Display key insights in a nice grid
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown("""
            <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #00ff88; margin: 0;'>✅ Analysis Complete</h3>
                <p style='color: #888; margin: 5px 0;'>Career path analyzed</p>
                <p style='font-size: 24px; color: white; margin: 10px 0;'><b>{}</b></p>
            </div>
        """.format(selected_category), unsafe_allow_html=True)
    
    with insight_col2:
        cities_analyzed = len(filtered_data)
        st.markdown("""
            <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #667eea; margin: 0;'>🌎 Cities Analyzed</h3>
                <p style='color: #888; margin: 5px 0;'>Location opportunities</p>
                <p style='font-size: 24px; color: white; margin: 10px 0;'><b>{}</b></p>
            </div>
        """.format(cities_analyzed), unsafe_allow_html=True)
    
    with insight_col3:
        # If AI analysis was done, show resume score
        if st.session_state.get('ai_results'):
            ai_data = st.session_state['ai_results']
            # Extract a score if available
            score_display = "✨ AI-Powered"
        else:
            score_display = "📊 Ready"
        
        st.markdown("""
            <div style='background-color: #1E2130; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #ff4b4b; margin: 0;'>🎯 Status</h3>
                <p style='color: #888; margin: 5px 0;'>Your profile</p>
                <p style='font-size: 24px; color: white; margin: 10px 0;'><b>{}</b></p>
            </div>
        """.format(score_display), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("📊 View Detailed Data", use_container_width=True):
            st.session_state['nav_to_tab'] = 'Map View'
            st.info("👇 Scroll down to the 'Map View' tab and click 'See the math behind your score'")
    
    with col_btn2:
        if st.button("💰 Explore Budget Lab", use_container_width=True):
            st.session_state['nav_to_tab'] = 'Budget Lab'
            st.info("👇 Check out the 'Budget Lab' tab for detailed financial breakdown")
    
    with col_btn3:
        if uploaded_file:
            if st.button("📄 Resume Analysis", use_container_width=True):
                st.session_state['nav_to_tab'] = 'Resume Pivot'
                st.info("👇 Go to 'Resume Pivot' tab for your full resume analysis")
    
    # Clear the results flag so it doesn't show every time
    if st.button("✅ Got it! (Close this message)", type="primary"):
        st.session_state['show_results'] = False
        st.rerun()

st.divider()

# --- TABBED INTERFACE ---
tab1, tab2, tab3 = st.tabs(["Map View", "Budget Lab", "Resume Pivot"])

# ========== TAB 1: MAP VIEW ==========
with tab1:
    st.subheader(f"Where can a {selected_category} thrive?")
    
    # Use filtered data (we already checked it's not empty earlier)
    map_data = filtered_data
    
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
    
    # Enhanced scatter geo map using Salary for size and color
    hover_data_dict = {
        'Salary': ':$,.0f',
        'Rent': ':$,.0f',
        'COL': True,
        'State': True,
        'Lat': False,
        'Lon': False
    }
    
    fig_map = px.scatter_geo(
        map_data,
        lat="Lat",
        lon="Lon",
        size="Salary",
        color="Salary",
        hover_name="City",
        hover_data=hover_data_dict,
        color_continuous_scale="Viridis",
        size_max=30,
        scope="usa",
        title=f"Best Cities for {selected_category}"
    )
    
    fig_map.update_layout(
        height=600,
        geo=dict(
            bgcolor='#0E1117',
            lakecolor='#1E2130',
            landcolor='#1E2130',
            showlakes=True,
            showcountries=True,
            countrycolor='#2E3440'
        ),
        paper_bgcolor='#0E1117',
        plot_bgcolor='#0E1117',
        font=dict(color='white')
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
    
    # Add city selector for deep dive analysis
    target_city = st.selectbox('🎯 Analyze a City', filtered_data['City'].unique())
    
    # Get the specific city data
    city_data = filtered_data[filtered_data['City'] == target_city].iloc[0]
    
    # Extract city-specific values
    city_salary = city_data['Salary']
    city_rent = city_data['Rent']
    city_state = city_data['State']
    city_col = city_data['COL']
    
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
            st.success(f"💰 In **{target_city}**, you will have **${monthly_savings:,.2f}** left over for fun/investing each month.")
        else:
            st.error(f"⚠️ In **{target_city}**, you may overspend by **${abs(monthly_savings):,.2f}** per month with a {lifestyle} lifestyle.")
    
    # Right Column: Success Checklist & Updated Metrics
    with right_col:
        st.markdown("### 📊 Key Financial Metrics")
        
        # Display key metrics
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Monthly Net Pay", f"${monthly_net:,.0f}", "After taxes")
            st.metric("Monthly Expenses", f"${(city_rent + lifestyle_cost + monthly_loan_payment):,.0f}", "Total")
        with col_b:
            st.metric("Projected Savings", f"${monthly_savings:,.0f}/mo", 
                     "💰" if monthly_savings > 1000 else ("⚠️" if monthly_savings < 0 else "📊"))
            st.metric("Annual Savings", f"${monthly_savings * 12:,.0f}/yr", "If consistent")
        
        st.divider()
        
        st.markdown("### Success Checklist")
        st.markdown("Track your financial milestones:")
        
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
    
    # --- DISPLAY AI RESULTS IF AVAILABLE ---
    if st.session_state.get('ai_results') and uploaded_file:
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