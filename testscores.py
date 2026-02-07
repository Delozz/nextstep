"""
Test the NEW Thriving Score Formula
Shows that cities now get realistic, differentiated scores
"""

from src.loader import load_all_salaries
from src.logic import calculate_taxes, calculate_thriving_score

# Test parameters
career = "Software Engineer"
debt = 30000
lifestyle = "Balanced"

# Load and filter data
df = load_all_salaries()
filtered = df[df['Category'] == career].copy()

print("=" * 90)
print(f"THRIVING SCORES FOR {career} | Debt: ${debt:,} | Lifestyle: {lifestyle}")
print("=" * 90)

# Calculate scores for all cities
results = []
for _, row in filtered.iterrows():
    # Calculate monthly net after taxes
    monthly_net = calculate_taxes(row['Salary'], row['State'])
    
    # Subtract loan payment
    loan_payment = (debt / 10000) * 115 if debt > 0 else 0
    monthly_net -= loan_payment
    
    # Calculate thriving score
    score = calculate_thriving_score(monthly_net, row['Rent'], row['COL'])
    
    results.append({
        'City': row['City'],
        'State': row['State'],
        'Salary': row['Salary'],
        'Rent': row['Rent'],
        'COL': row['COL'],
        'Net_After_All': int(monthly_net),
        'Score': score
    })

# Sort by score (best first)
results = sorted(results, key=lambda x: x['Score'], reverse=True)

print(f"\n{'Rank':<6}{'City':<20}{'Salary':<12}{'Rent':<10}{'COL':<8}{'Net/Mo':<12}{'Score':<8}")
print("-" * 90)

for i, city in enumerate(results, 1):
    emoji = "🏆" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
    print(f"{emoji} {i:<4}{city['City']:<20}${city['Salary']:>10,}  ${city['Rent']:>6,}  "
        f"{city['COL']:>5}  ${city['Net_After_All']:>8,}  {city['Score']:>5}/100")

print("\n" + "=" * 90)
print("KEY INSIGHTS:")
print("=" * 90)

top3 = results[:3]
print(f"\n🏆 TOP 3 CITIES:")
for i, city in enumerate(top3, 1):
    savings = city['Net_After_All'] - city['Rent']
    rent_pct = (city['Rent'] / (city['Net_After_All'] + city['Rent'])) * 100
    print(f"\n{i}. {city['City']}, {city['State']} (Score: {city['Score']}/100)")
    print(f"   • Salary: ${city['Salary']:,}/year")
    print(f"   • Take-home: ${city['Net_After_All']:,}/month (after taxes & loans)")
    print(f"   • Rent: ${city['Rent']:,}/month ({rent_pct:.1f}% of income)")
    print(f"   • Left over: ${savings:,}/month for savings/fun")
    print(f"   • COL Index: {city['COL']} (lower = your $ goes further)")

print("\n" + "=" * 90)

# Show San Francisco specifically
sf = next((c for c in results if c['City'] == 'San Francisco'), None)
if sf:
    sf_rank = results.index(sf) + 1
    print(f"\n📍 SAN FRANCISCO BREAKDOWN:")
    print(f"   Rank: #{sf_rank} out of {len(results)}")
    print(f"   Score: {sf['Score']}/100")
    print(f"   Why lower? High rent (${sf['Rent']:,}) = {(sf['Rent']/(sf['Net_After_All']+sf['Rent'])*100):.1f}% of income")
    print(f"   High COL ({sf['COL']}) means your money doesn't go as far")

print("\n" + "=" * 90)
print("✅ Scores now properly differentiate cities based on YOUR situation!")
print("=" * 90)