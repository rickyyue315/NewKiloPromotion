import pandas as pd
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dispatch_logic():
    """Test the dispatch type logic with various scenarios"""
    
    # Import the determine_dispatch_type function from promo_calculator
    from promo_calculator import determine_dispatch_type
    
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