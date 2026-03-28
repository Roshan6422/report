"""
Test station name cleaning to remove extra province/division text
"""
import re

def clean_station_name(station_raw):
    """Clean station name - remove extra text"""
    # Remove "POLICE STATION" suffix
    station = re.sub(r'\s*(?:POLICE\s*)?STATION\s*$', '', station_raw, flags=re.IGNORECASE)
    
    # Remove any "Div, S/DIG PROVINCE" text that might be added
    station = re.sub(r',?\s*(?:Div|Division).*?(?:S/DIG|SDIG).*?PROVINCE', '', station, flags=re.IGNORECASE)
    
    # Remove leading/trailing commas and spaces
    station = station.strip(' ,')
    
    return station.upper()

# Test cases
test_cases = [
    "Div, S/DIG SABARAGAMUWA PROVINCE, EMBILIPITIYA",
    "EMBILIPITIYA",
    "Embilipitiya Police Station",
    "UDAWALAWA Div, S/DIG SABARAGAMUWA PROVINCE",
    "ADAMPAN",
    "Colombo Fort Police Station"
]

print("Testing station name cleaning:")
print("=" * 70)
for test in test_cases:
    cleaned = clean_station_name(test)
    print(f"Input:  {test}")
    print(f"Output: {cleaned}")
    print("-" * 70)
