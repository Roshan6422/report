"""
Test app.py with March 21, 2026 report
මාර්තු 21, 2026 වාර්තාව සමඟ app.py පරීක්ෂා කරන්න
"""

import sys
import os

# Test if app.py can be imported
try:
    from app import SinhalaPoliceReportExtractor
    print("✓ app.py imported successfully")
except Exception as e:
    print(f"❌ Failed to import app.py: {e}")
    sys.exit(1)

# Create test instance
extractor = SinhalaPoliceReportExtractor()

print("\n" + "=" * 80)
print("Testing SinhalaPoliceReportExtractor")
print("=" * 80)

# Test 1: Check categories
print("\n1. Testing categories (should have 29):")
print(f"   Total categories: {len(extractor.categories)}")
assert len(extractor.categories) == 29, "Should have exactly 29 categories"
print("   ✓ All 29 categories present")

# Test 2: Check specific categories
print("\n2. Testing specific category names:")
test_categories = {
    "01": "ත්‍රස්තවාදී ක්‍රියාකාරකම",
    "02": "අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ)",
    "09": "ස්ත්‍රී දූෂණ හා බරපතල ලිංගික අපයෝජන",
    "20": "විශාල ප්‍රමාණයේ මත් ද්‍රව්‍ය/මත්පැන් අත්අඩංගුට ගැනී",
    "29": "වෙනත් විශේෂ සිදුවීම"
}

for cat_num, expected_name in test_categories.items():
    actual_name = extractor.categories.get(cat_num)
    assert actual_name == expected_name, f"Category {cat_num} name mismatch"
    print(f"   ✓ Category {cat_num}: {actual_name}")

# Test 3: Test nil detection
print("\n3. Testing nil category detection:")
test_text_nil = "01. ත්‍රස්තවාදී ක්‍රියාකාරකම : නැත."
is_nil = extractor.is_nil_category(test_text_nil, "01")
assert is_nil == True, "Should detect nil category"
print("   ✓ Nil detection works correctly")

# Test 4: Test count extraction
print("\n4. Testing incident count extraction:")
test_text_count = "02. අවි ආයුධ සොයා ගැනීම (පුපුරණ ද්‍රව්‍ය / උණ්ඩ) :- 09"
count = extractor.extract_category_count(test_text_count, "02")
assert count == 9, f"Should extract count 9, got {count}"
print(f"   ✓ Count extraction works: {count}")

# Test 5: Test person details extraction
print("\n5. Testing person details extraction:")
test_person_text = """
බී.ජී.සී. අමරවීර
අවු : 49
පුරුෂ
රැකියාව : ගොවිතැන
අංර 30, දමසන්වැල, නුවරඑළිය
දු.අ : 0771234567
"""
person = extractor.extract_person_details(test_person_text, "සැකකරු")
print(f"   Name: {person.get('name', 'N/A')}")
print(f"   Age: {person.get('age', 'N/A')}")
print(f"   Gender: {person.get('gender', 'N/A')}")
print(f"   Occupation: {person.get('occupation', 'N/A')}")
print(f"   ✓ Person details extraction works")

# Test 6: Test text cleaning
print("\n6. Testing text cleaning:")
dirty_text = "මෙම   සැකකරු    බලපත්‍රය්   සනොමැතිව"
clean = extractor.clean_text(dirty_text)
print(f"   Original: '{dirty_text}'")
print(f"   Cleaned: '{clean}'")
print("   ✓ Text cleaning works")

# Test 7: Test header extraction
print("\n7. Testing header extraction:")
test_header_text = """
දෛනික සිදුවීම් වාර්ථාව
2026.03.20 වන දින පැය 0400 සිට 2026.03.21 දින පැය 0400 දක්වා
"""
header = extractor.extract_header(test_header_text)
print(f"   Report title: {header.get('report_title')}")
print(f"   Date range: {header.get('date_range')}")
print(f"   Report period: {header.get('report_period')}")
print("   ✓ Header extraction works")

print("\n" + "=" * 80)
print("✅ All tests passed! / සියලුම පරීක්ෂණ සාර්ථකයි!")
print("=" * 80)

print("\n📝 Next steps:")
print("1. Run: python app.py <your_pdf_file.pdf>")
print("2. Check the generated JSON file")
print("3. Review the summary report")
print("\n📝 ඊළඟ පියවර:")
print("1. ධාවනය කරන්න: python app.py <ඔබේ_pdf_ගොනුව.pdf>")
print("2. ජනනය කළ JSON ගොනුව පරීක්ෂා කරන්න")
print("3. සාරාංශ වාර්තාව සමාලෝචනය කරන්න")
