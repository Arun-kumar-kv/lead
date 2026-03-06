"""
Test script to verify conversion rate calculation
Run this to see what's happening
"""

# Simulate your exact data
conversion_breakdown = {
    "total_leads": 7,
    "new_lead": 5,
    "prospect": 0,
    "oppurtunity": 0,
    "converted_to_tenant": 2
}

total_leads = 7

# Your current code
converted = conversion_breakdown.get("converted_to_tenant", 0)
print(f"converted value: {converted}")
print(f"converted type: {type(converted)}")

overall_conversion_rate = (
    round((converted / total_leads) * 100, 2)
    if total_leads > 0 else 0.0
)

print(f"Calculation: ({converted} / {total_leads}) * 100 = {overall_conversion_rate}")
print(f"Expected: 28.57")
print(f"Got: {overall_conversion_rate}")

# Check if there's something wrong
if overall_conversion_rate == 0:
    print("\n❌ ISSUE FOUND!")
    print(f"converted == 0: {converted == 0}")
    print(f"total_leads == 0: {total_leads == 0}")
    print(f"Check your actual service code - something is overriding this")
else:
    print("\n✅ Calculation works correctly!")