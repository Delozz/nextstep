# src/loader.py
import pandas as pd
import streamlit as st
import os

# --- CONFIGURATION ---
CAREER_BASE_SALARIES = {
    'Software Engineer': 100000,
    'Data Scientist': 90000,
    'Cybersecurity Analyst': 90000,
    'UX Designer': 80000,
    'Product Manager': 110000,
    'Machine Learning Engineer': 110000,
    'Cloud Architect': 90000,
    'Data Engineer': 90000,
    'DevOps Engineer': 95000
}

# Tier Multipliers (Higher Tier = Higher Salary)
TIER_MULTIPLIERS = {
    1: 1.2,  # SF, NYC
    2: 1.15,  # Austin, Denver
    3: 1.0,  # Raleigh, SLC
    4: 1.0   # College Towns
}

BASE_CITIES = [
    # Tier 1 - High-cost tech hubs
    {'City': 'San Francisco', 'State': 'CA', 'Tier': 1, 'Lat': 37.77, 'Lon': -122.41, 'Rent': 3200, 'COL': 96, 'Rent_Index': 3200, 'COL_Index': 96},
    {'City': 'New York', 'State': 'NY', 'Tier': 1, 'Lat': 40.71, 'Lon': -74.00, 'Rent': 3600, 'COL': 100, 'Rent_Index': 3600, 'COL_Index': 100},
    {'City': 'Seattle', 'State': 'WA', 'Tier': 1, 'Lat': 47.60, 'Lon': -122.33, 'Rent': 2300, 'COL': 85, 'Rent_Index': 2300, 'COL_Index': 85},
    {'City': 'Boston', 'State': 'MA', 'Tier': 1, 'Lat': 42.36, 'Lon': -71.05, 'Rent': 2700, 'COL': 88, 'Rent_Index': 2700, 'COL_Index': 88},
    
    # Tier 2 - Growing tech cities
    {'City': 'Austin', 'State': 'TX', 'Tier': 2, 'Lat': 30.26, 'Lon': -97.74, 'Rent': 1700, 'COL': 65, 'Rent_Index': 1700, 'COL_Index': 65},
    {'City': 'Denver', 'State': 'CO', 'Tier': 2, 'Lat': 39.73, 'Lon': -104.99, 'Rent': 1900, 'COL': 68, 'Rent_Index': 1900, 'COL_Index': 68},
    {'City': 'Chicago', 'State': 'IL', 'Tier': 2, 'Lat': 41.87, 'Lon': -87.62, 'Rent': 2000, 'COL': 70, 'Rent_Index': 2000, 'COL_Index': 70},
    {'City': 'Atlanta', 'State': 'GA', 'Tier': 2, 'Lat': 33.74, 'Lon': -84.38, 'Rent': 1800, 'COL': 66, 'Rent_Index': 1800, 'COL_Index': 66},
    {'City': 'Portland', 'State': 'OR', 'Tier': 2, 'Lat': 45.52, 'Lon': -122.67, 'Rent': 1850, 'COL': 67, 'Rent_Index': 1850, 'COL_Index': 67},

    # Tier 3 - Affordable mid-size cities
    {'City': 'Raleigh', 'State': 'NC', 'Tier': 3, 'Lat': 35.77, 'Lon': -78.63, 'Rent': 1400, 'COL': 63, 'Rent_Index': 1400, 'COL_Index': 63},
    {'City': 'Huntsville', 'State': 'AL', 'Tier': 3, 'Lat': 34.73, 'Lon': -86.58, 'Rent': 1100, 'COL': 55, 'Rent_Index': 1100, 'COL_Index': 55},
    {'City': 'Columbus', 'State': 'OH', 'Tier': 3, 'Lat': 39.96, 'Lon': -82.99, 'Rent': 1200, 'COL': 58, 'Rent_Index': 1200, 'COL_Index': 58},
    {'City': 'Salt Lake City', 'State': 'UT', 'Tier': 3, 'Lat': 40.76, 'Lon': -111.89, 'Rent': 1300, 'COL': 60, 'Rent_Index': 1300, 'COL_Index': 60},
    
    # Tier 4 - College towns and low-cost areas
    {'City': 'College Station', 'State': 'TX', 'Tier': 4, 'Lat': 30.62, 'Lon': -96.33, 'Rent': 900, 'COL': 50, 'Rent_Index': 900, 'COL_Index': 50},
    {'City': 'Ann Arbor', 'State': 'MI', 'Tier': 4, 'Lat': 42.28, 'Lon': -83.74, 'Rent': 1300, 'COL': 62, 'Rent_Index': 1300, 'COL_Index': 62},
    {'City': 'Madison', 'State': 'WI', 'Tier': 4, 'Lat': 43.07, 'Lon': -89.40, 'Rent': 1250, 'COL': 60, 'Rent_Index': 1250, 'COL_Index': 60},
]

@st.cache_data
def load_all_salaries():
    """
    Generates the Cross-Product of Cities X Careers.
    Returns DataFrame with all necessary fields for the app.
    """
    data = []
    
    for city in BASE_CITIES:
        for career, base_salary in CAREER_BASE_SALARIES.items():
            
            # Calculate Localized Salary
            tier_adjust = TIER_MULTIPLIERS.get(city['Tier'], 1.0)
            projected_salary = int(base_salary * tier_adjust)
            
            data.append({
                'City': city['City'],
                'State': city['State'],
                'Lat': city['Lat'],
                'Lon': city['Lon'],
                'Rent': city['Rent'],
                'Rent_Index': city['Rent_Index'],
                'COL': city['COL'],
                'COL_Index': city['COL_Index'],
                'Category': career,
                'Role': career,  # Backward compatibility
                'Salary': projected_salary,
                'Tier': city['Tier']
            })
            
    return pd.DataFrame(data)

def load_data():
    """Alias for backward compatibility with test_backend.py"""
    return load_all_salaries()
