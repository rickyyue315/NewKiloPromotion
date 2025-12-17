import pandas as pd
from promo_calculator import Config, calculate_demand

def test_dispatch_type_logic():
    """Test ND site Dispatch_Type logic"""
    
    # Create test data
    test_data = pd.DataFrame({
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'RP_Type': ['ND', 'ND', 'ND', 'ND'],
        'SaSa_Net_Stock': [50, 30, 20, 10],
        'Pending_Received': [0, 0, 0, 0],
        'Safety_Stock': [10, 10, 10, 10],
        'Last_Month_Sold_Qty_capped': [100, 80, 60, 40],
        'MOQ': [12, 12, 12, 12],
        'Supply_source': [1, 2, 4, 2],  # Different supply sources
        'SKU_Target': [100, 80, 60, 40],
        'Site_Target_%': [0.5, 0.5, 0.5, 0.5],
        'Is_Promo_SKU': [True, True, True, True],
        'Promo_Target_Cover_Days': [7, 7, 7, 7],
        'Promotion_Days': [5, 3, 6, 2],  # Different promotion days
    })
    
    # Calculate demand
    cfg = Config()
    result = calculate_demand(test_data, cfg)
    
    print("=== Test ND Site Dispatch_Type Logic ===")
    print("Site\tSupply\tDN_Qty\tDispatch_Type_Code\tRemark")
    print("-" * 70)
    
    for _, row in result.iterrows():
        # Replace Chinese characters with codes for display
        dispatch_type = row['Dispatch_Type']
        if dispatch_type == '開PO':
            dispatch_code = 'OPEN_PO'
        elif dispatch_type == '開DN':
            dispatch_code = 'OPEN_DN'
        elif dispatch_type == 'ND':
            dispatch_code = 'ND'
        else:
            dispatch_code = str(dispatch_type)
            
        remark = row['Dispatch_Remark']
        if remark == 'ND 派貨':
            remark_code = 'ND_DISPATCH'
        else:
            remark_code = str(remark)
            
        print(f"{row['Site']}\t{row['Supply_source']}\t{row['Suggested_DN_Qty']}\t{dispatch_code}\t\t{remark_code}")
    
    print("\n=== Expected Results ===")
    print("ND001: Supply_source=1, DN_Qty>0 -> Dispatch_Type should be OPEN_PO")
    print("ND002: Supply_source=2, DN_Qty>0 -> Dispatch_Type should be OPEN_DN") 
    print("ND003: Supply_source=4, DN_Qty>0 -> Dispatch_Type should be OPEN_PO")
    print("ND004: Supply_source=2, DN_Qty>0 -> Dispatch_Type should be OPEN_DN")
    print("\nAll ND sites should have Remark=ND_DISPATCH")
    
    # Verify results
    print("\n=== Verification ===")
    expected = ['OPEN_PO', 'OPEN_DN', 'OPEN_PO', 'OPEN_DN']
    actual = []
    
    for _, row in result.iterrows():
        dispatch_type = row['Dispatch_Type']
        if dispatch_type == '開PO':
            actual.append('OPEN_PO')
        elif dispatch_type == '開DN':
            actual.append('OPEN_DN')
        else:
            actual.append(str(dispatch_type))
    
    for i, (exp, act) in enumerate(zip(expected, actual)):
        status = "PASS" if exp == act else "FAIL"
        print(f"ND00{i+1}: Expected={exp}, Actual={act}, Status={status}")

if __name__ == "__main__":
    test_dispatch_type_logic()