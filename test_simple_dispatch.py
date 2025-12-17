import pandas as pd
from promo_calculator import Config

def test_dispatch_type_logic():
    """Direct test of Dispatch_Type logic"""
    
    config = Config()
    
    # Test cases: (Site, RP_Type, Supply_source, Suggested_DN_Qty, Expected_Type)
    test_cases = [
        ('ND001', 'ND', 1, 0, 'No replenishment needed'),
        ('ND002', 'ND', 2, 0, 'No replenishment needed'),
        ('ND003', 'ND', 4, 0, 'No replenishment needed'),
        ('ND004', 'ND', 2, 0, 'No replenishment needed'),
        ('ND005', 'ND', 1, 10, 'Open PO'),
        ('ND006', 'ND', 2, 20, 'DN required'),
        ('ND007', 'ND', 4, 15, 'Open PO'),
        ('D001', 'RF', 2, 0, 'D001'),
        ('RF001', 'RF', 1, 0, 'Buyer needs to order'),
        ('RF002', 'RF', 2, 0, 'DN required'),
        ('RF003', 'RF', 4, 0, 'Buyer needs to order'),
    ]
    
    print("Testing Dispatch_Type Logic:")
    print("=" * 80)
    
    for site, rp_type, supply_source, dn_qty, expected_type in test_cases:
        # Create test row
        test_row = {
            'Site': site,
            'RP_Type': rp_type,
            'Supply_source': supply_source,
            'Suggested_DN_Qty': dn_qty,
        }
        
        # Call determine_dispatch_type function logic
        result_type = determine_dispatch_type(test_row, config)
        
        # Check result
        if result_type == expected_type:
            print(f"[PASS] Site: {site}, RP: {rp_type}, Supply: {supply_source}, DN_Qty: {dn_qty}")
            print(f"   Result: {result_type} (Expected: {expected_type})")
        else:
            print(f"[FAIL] Site: {site}, RP: {rp_type}, Supply: {supply_source}, DN_Qty: {dn_qty}")
            print(f"   Result: {result_type} (Expected: {expected_type})")
        
        print()

def determine_dispatch_type(row: dict, config: Config) -> str:
    """
    Copy the determine_dispatch_type logic from promo_calculator.py
    """
    site = (row.get("Site") or "").upper()
    rp = (row.get("RP_Type") or "").upper()

    # Supply_source might be float/NaN; convert safely
    raw_supply = row.get("Supply_source", 0)
    try:
        supply = int(raw_supply) if pd.notna(raw_supply) else 0
    except (TypeError, ValueError):
        supply = 0

    # Check if Suggested_DN_Qty > 0 for ND sites
    suggested_dn_qty = row.get("Suggested_DN_Qty", 0)
    try:
        dn_qty = float(suggested_dn_qty) if pd.notna(suggested_dn_qty) else 0
    except (TypeError, ValueError):
        dn_qty = 0

    if site == config.DC_SITE_CODE:
        return "D001"
    if rp == "ND":
        if dn_qty > 0:
            # For ND sites with DN Qty > 0, use Supply_source to determine
            if supply in (1, 4):
                return "Open PO"
            elif supply == 2:
                return "DN required"
            else:
                return "ND"
        else:
            # For ND sites with DN Qty = 0, show "No replenishment needed"
            return "No replenishment needed"
    if supply in (1, 4):
        return "Buyer needs to order"
    if supply == 2:
        return "DN required"
    return "N/A"

if __name__ == "__main__":
    test_dispatch_type_logic()