import sys
import os

# Set encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add path to find modules
sys.path.append(r"d:\PROJECTS\pdf convert tool")

try:
    from station_mapping import SINHALA_TO_ENGLISH as S2E_STATION
    from police_geo_utils import SINHALA_TO_ENGLISH as S2E_GEO
    
    print(f"Station mapping entries: {len(S2E_STATION)}")
    print(f"Geo utils mapping entries: {len(S2E_GEO)}")
    
    unique_to_geo = {}
    for k, v in S2E_GEO.items():
        if k not in S2E_STATION:
            unique_to_geo[k] = v
            
    print(f"\nUnique entries in police_geo_utils ({len(unique_to_geo)}):")
    # Sort for cleaner output
    for k in sorted(unique_to_geo.keys()):
        v = unique_to_geo[k]
        print(f"    '{k}': '{v}',")
        
except Exception as e:
    import traceback
    traceback.print_exc()
