#!/usr/bin/env python3
"""
JSON Repair Tool - Fix common AI JSON errors
"""

import json
import os
import re


def repair_json(json_str):
    """
    Attempt to repair common JSON errors from AI responses.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Repaired JSON string or None if unrepairable
    """
    if not json_str or len(json_str.strip()) < 2:
        return None

    repaired = json_str.strip()

    # Remove markdown code blocks
    repaired = re.sub(r'```json\s*', '', repaired)
    repaired = re.sub(r'```\s*', '', repaired)
    repaired = repaired.strip()

    # Extract JSON object
    if "{" in repaired:
        start = repaired.find("{")
        end = repaired.rfind("}") + 1
        repaired = repaired[start:end]

    # Fix 1: Remove trailing commas before closing brackets
    repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)

    # Fix 2: Add missing commas between array elements
    repaired = re.sub(r'}\s*{', '},{', repaired)
    repaired = re.sub(r']\s*\[', '],[', repaired)

    # Fix 3: Fix line breaks inside strings (common issue)
    # Replace newlines inside quoted strings with spaces
    def fix_string_breaks(match):
        content = match.group(1)
        # Replace newlines with spaces inside the string
        fixed = content.replace('\n', ' ').replace('\r', ' ')
        return f'"{fixed}"'

    # This regex finds quoted strings and fixes line breaks in them
    repaired = re.sub(r'"([^"]*(?:\n[^"]*)*)"', fix_string_breaks, repaired)

    # Fix 4: Add missing closing quotes for strings
    # Find patterns like: "key": "value without closing quote,
    repaired = re.sub(r':\s*"([^"]*?)(?=,\s*"|\s*})', r': "\1"', repaired)

    # Fix 5: Replace single quotes used as JSON delimiters (not apostrophes in text)
    # Only replace when the pattern looks like a key-value pair, not mid-word apostrophes
    repaired = re.sub(r"(?<=[:,\[{])\s*'([^'\\]*(?:\\.[^'\\]*)*)'\s*(?=[,\]}:])", r' "\1"', repaired)

    # Fix 6: Remove comments (// or /* */)
    repaired = re.sub(r'//.*?$', '', repaired, flags=re.MULTILINE)
    repaired = re.sub(r'/\*.*?\*/', '', repaired, flags=re.DOTALL)

    # Fix 7: Fix unquoted keys
    # Match word characters followed by colon
    repaired = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', repaired)

    # Fix 8: Remove duplicate commas
    repaired = re.sub(r',+', ',', repaired)

    # Fix 9: Aggressively close opened delimiters
    # Count open/close braces
    open_braces = repaired.count('{')
    close_braces = repaired.count('}')
    if open_braces > close_braces:
        # If a string is open, close it first
        if repaired.count('"') % 2 != 0:
            repaired += '"'
        repaired += '}' * (open_braces - close_braces)

    return repaired


def validate_police_json(data):
    """
    Validate that JSON has required police report structure.
    
    Args:
        data: Parsed JSON dict
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Root must be an object"

    if "categories" not in data:
        return False, "Missing 'categories' key"

    categories = data["categories"]
    if not isinstance(categories, dict):
        return False, "'categories' must be an object"

    # Check for all 29 official table categories (01–29)
    for i in range(1, 30):
        key = str(i).zfill(2)
        if key not in categories:
            return False, f"Missing category '{key}'"

        val = categories[key]
        if isinstance(val, dict):
            if "incidents" not in val:
                return False, f"Category '{key}' object must include 'incidents'"
        elif not isinstance(val, list):
            return False, f"Category '{key}' must be an array or {{incidents: ...}}"

    # Check counts if present
    if "counts" in data:
        counts = data["counts"]
        if not isinstance(counts, dict):
            return False, "'counts' must be an object"

    return True, "Valid"


def validate_incident_schema(data):
    """
    Validate that JSON has the 8-field incident extraction structure.
    
    Expected fields: date, time, station, province, district, 
    category_num, category_name, description.
    """
    if not isinstance(data, dict):
        return False, "Root must be an object"

    required_fields = [
        "date", "time", "station", "province", "district",
        "category_num", "category_name", "description"
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"

    return True, "Valid"


def create_minimal_structure():
    """Create minimal valid police report JSON structure."""
    return {
        "categories": {str(i).zfill(2): [] for i in range(1, 30)},
        "counts": {str(i).zfill(2): 0 for i in range(1, 30)},
        "report_date_range": "No date information available"
    }


def safe_parse_json(json_str, fallback_to_minimal=True):
    """
    Safely parse JSON with automatic repair attempts.
    
    Args:
        json_str: JSON string to parse
        fallback_to_minimal: If True, return minimal structure on failure
        
    Returns:
        Parsed JSON dict or None
    """
    if not json_str:
        return create_minimal_structure() if fallback_to_minimal else None

    # Try 1: Direct parse
    try:
        data = json.loads(json_str)
        is_valid, msg = validate_police_json(data)
        if is_valid:
            return data
        print(f"  ⚠️ JSON validation failed: {msg}")
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error: {e.msg} at line {e.lineno}, col {e.colno}")

    # Try 2: Repair and parse
    print("  🔧 Attempting JSON repair (method 1)...")
    repaired = repair_json(json_str)
    if repaired:
        try:
            data = json.loads(repaired)
            is_valid, msg = validate_police_json(data)
            if is_valid:
                print("  ✅ JSON repaired successfully!")
                return data
            print(f"  ⚠️ Repaired JSON validation failed: {msg}")
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Repaired JSON still invalid: {e.msg} at line {e.lineno}, col {e.colno}")

    # Try 3: Aggressive repair - fix specific error location
    print("  🔧 Attempting aggressive repair (method 2)...")
    try:
        # Try to parse and get exact error location
        json.loads(json_str)
    except json.JSONDecodeError as e:
        # We know where the error is, try to fix it
        lines = json_str.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            print(f"     Error at line {e.lineno}: {error_line[:80]}")

            # Common fix: add missing comma or quote
            if "delimiter" in e.msg.lower():
                # Try adding comma at error position
                fixed_line = error_line[:e.colno-1] + ',' + error_line[e.colno-1:]
                lines[e.lineno - 1] = fixed_line
                fixed_json = '\n'.join(lines)

                try:
                    data = json.loads(fixed_json)
                    is_valid, msg = validate_police_json(data)
                    if is_valid:
                        print("  ✅ Aggressive repair succeeded!")
                        return data
                except (json.JSONDecodeError, ValueError):
                    pass

    # Try 4: Use Python's json.tool to format and identify issues
    print("  🔧 Attempting format-based repair (method 3)...")
    temp_path = None
    try:
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_str)
            temp_path = f.name

        # Try to format with json.tool (it's more lenient)
        result = subprocess.run(
            ['python', '-m', 'json.tool', temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            is_valid, msg = validate_police_json(data)
            if is_valid:
                print("  ✅ Format-based repair succeeded!")
                return data
    except Exception:
        pass
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    # Try 5: Fallback to minimal structure
    if fallback_to_minimal:
        print("  ⚠️ All repair attempts failed, using minimal fallback structure")
        return create_minimal_structure()

    return None


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Valid JSON
        '{"categories": {"01": [], "02": []}, "counts": {"01": 0, "02": 0}}',

        # Trailing comma
        '{"categories": {"01": [], "02": [],}, "counts": {"01": 0,}}',

        # Single quotes
        "{'categories': {'01': []}, 'counts': {'01': 0}}",

        # Unquoted keys
        '{categories: {01: []}, counts: {01: 0}}',

        # Missing commas
        '{"categories": {"01": [] "02": []}}',
    ]

    print("Testing JSON Repair Tool")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input:  {test[:50]}...")
        result = safe_parse_json(test)
        if result:
            print("Result: ✅ Parsed successfully")
        else:
            print("Result: ❌ Failed to parse")
