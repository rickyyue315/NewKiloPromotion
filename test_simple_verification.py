import pandas as pd

def determine_dispatch_type(row) -> str:
    """
    Simplified version of determine_dispatch_type function for testing
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

    if site == "D001":
        return "D001"
    if rp == "ND":
        # 確保 Suggested_DN_Qty 為 0 時絕對顯示 "無須補貨"
        if dn_qty > 0:
            # For ND sites with DN Qty > 0, use Supply_source to determine
            # 顯示"開PO"或"需生成 DN"而不是"ND"，因為Dispatch_Remark已有"ND派貨"提示
            if supply in (1, 4):
                return "開PO"
            elif supply == 2:
                return "需生成 DN"
            else:
                return "ND"
        else:
            # For ND sites with DN Qty = 0, show "無須補貨"
            # 確保即使有其他因素影響，DN Qty = 0 時也顯示 "無須補貨"
            return "無須補貨"
    if supply in (1, 4):
        return "Buyer需要訂貨"
    if supply == 2:
        return "需生成 DN"
    return "N/A"

def test_dispatch_logic():
    """Test the dispatch type logic with various scenarios"""
    
    # Test cases
    test_cases = [
        # Case 1: ND site with Suggested_DN_Qty = 0, Supply_source = 2
        {
            "Site": "ND001",
            "RP_Type": "ND",
            "Supply_source": 2,
            "Suggested_DN_Qty": 0,
            "expected": "無須補貨"
        },
        # Case 2: ND site with Suggested_DN_Qty = 0, Supply_source = 1
        {
            "Site": "ND002",
            "RP_Type": "ND",
            "Supply_source": 1,
            "Suggested_DN_Qty": 0,
            "expected": "無須補貨"
        },
        # Case 3: ND site with Suggested_DN_Qty = 0, Supply_source = 4
        {
            "Site": "ND003",
            "RP_Type": "ND",
            "Supply_source": 4,
            "Suggested_DN_Qty": 0,
            "expected": "無須補貨"
        },
        # Case 4: ND site with Suggested_DN_Qty > 0, Supply_source = 2
        {
            "Site": "ND004",
            "RP_Type": "ND",
            "Supply_source": 2,
            "Suggested_DN_Qty": 50,
            "expected": "需生成 DN"
        },
        # Case 5: ND site with Suggested_DN_Qty > 0, Supply_source = 1
        {
            "Site": "ND005",
            "RP_Type": "ND",
            "Supply_source": 1,
            "Suggested_DN_Qty": 30,
            "expected": "開PO"
        },
        # Case 6: D001 site
        {
            "Site": "D001",
            "RP_Type": "ND",
            "Supply_source": 2,
            "Suggested_DN_Qty": 0,
            "expected": "D001"
        },
        # Case 7: Non-ND site with Supply_source = 2
        {
            "Site": "H001",
            "RP_Type": "RP",
            "Supply_source": 2,
            "Suggested_DN_Qty": 0,
            "expected": "需生成 DN"
        }
    ]
    
    print("Testing Dispatch_Type Logic:")
    print("=" * 80)
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        # Create a DataFrame row
        row = pd.Series(case)
        
        # Get the actual result
        actual = determine_dispatch_type(row)
        expected = case["expected"]
        
        # Check if the test passed
        passed = actual == expected
        if not passed:
            all_passed = False
        
        # Print the test result
        status = "PASS" if passed else "FAIL"
        print(f"Test {i}: {status}")
        print(f"  Site: {case['Site']}, RP_Type: {case['RP_Type']}, Supply_source: {case['Supply_source']}")
        print(f"  Suggested_DN_Qty: {case['Suggested_DN_Qty']}")
        print(f"  Expected: {expected}, Actual: {actual}")
        print()
    
    print("=" * 80)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    test_dispatch_logic()