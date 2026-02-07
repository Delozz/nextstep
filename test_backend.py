# test_backend.py
from src.loader import load_data
from src.logic import calculate_net_monthly, get_thriving_score

print("Loading Data...")
df = load_data()

print(f"✅ Loaded {len(df)} rows of data.")
print("Sample Cities:", df['City'].unique()[:5])

# Pick a random row to test math
if not df.empty:
    sample = df.iloc[0]
    salary = sample['Salary']
    rent = sample['Rent_Index']
    col = sample['COL_Index']
    
    net = calculate_net_monthly(salary, debt_amount=30000)
    score = get_thriving_score(net, rent, col)
    
    print(f"\n--- TEST CASE: {sample['City']} ---")
    print(f"Role: {sample['Role']}")
    print(f"Salary: ${salary:,.0f}")
    print(f"Net Monthly: ${net:,.2f}")
    print(f"Thriving Score: {score}/100")
else:
    print("❌ DataFrame is empty. Check your CSV column names!")