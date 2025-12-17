import pandas as pd
from promo_calculator import Config, calculate_demand

def test_updated_dispatch_logic():
    """Test updated Dispatch_Type logic"""
    
    # Create test data with different scenarios
    test_data = pd.DataFrame({
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005', 'TEST006'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004', 'ND005', 'D001'],
        'RP_Type': ['ND', 'ND', 'ND', 'ND', 'ND', 'RF'],
        'SaSa_Net_Stock': [50, 30, 20, 10, 100, 200],
        'Pending_Received': [0, 0, 0, 0, 0, 0],
        'Safety_Stock': [10, 10, 10, 10, 10, 10],
        'Last_Month_Sold_Qty_capped': [100, 80, 60, 40, 0, 50],
        'MOQ': [12, 12, 12, 12, 12, 12],
        'Supply_source': [1, 2, 4, 2, 2, 2],  # Different supply sources
        'SKU_Target': [100, 80, 60, 40, 0, 50],  # TEST005 has no target
        'Site_Target_%': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        'Is_Promo_SKU': [True, True, True, True, False, True],
        'Promo_Target_Cover_Days': [7, 7, 7, 7, 7, 7],
        'Promotion_Days': [5, 3, 6, 2, 1, 4],  # Different promotion days
    })
    
    # Calculate demand
    cfg = Config()
    result = calculate_demand(test_data, cfg)
    
    print("=== Test Updated Dispatch_Type Logic ===")
    print("Site\tSupply\tDN_Qty\tDispatch_Type_Code\tRemark")
    print("-" * 70)
    
    for _, row in result.iterrows():
        # Replace Chinese characters with codes for display
        dispatch_type = row['Dispatch_Type']
        if dispatch_type == '開PO':
            dispatch_code = 'OPEN_PO'
        elif dispatch_type == '需生成 DN':
            dispatch_code = 'GENERATE_DN'
        elif dispatch_type == '無須補貨':
            dispatch_code = 'NO_REPLENISH'
        elif dispatch_type == 'ND':
            dispatch_code = 'ND'
        elif dispatch_type == 'D001':
            dispatch_code = 'D001'
        elif dispatch_type == 'Buyer需要訂貨':
            dispatch_code = 'BUYER_ORDER'
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
    print("ND002: Supply_source=2, DN_Qty>0 -> Dispatch_Type should be GENERATE_DN") 
    print("ND003: Supply_source=4, DN_Qty>0 -> Dispatch_Type should be OPEN_PO")
    print("ND004: Supply_source=2, DN_Qty>0 -> Dispatch_Type should be GENERATE_DN")
    print("ND005: Supply_source=2, DN_Qty=0 -> Dispatch_Type should be NO_REPLENISH")
    print("D001: Site=D001 -> Dispatch_Type should be D001")
    
    # Verify results
    print("\n=== Verification ===")
    expected = ['OPEN_PO', 'GENERATE_DN', 'OPEN_PO', 'GENERATE_DN', 'NO_REPLENISH', 'D001']
    actual = []
    
    for _, row in result.iterrows():
        dispatch_type = row['Dispatch_Type']
        if dispatch_type == '開PO':
            actual.append('OPEN_PO')
        elif dispatch_type == '需生成 DN':
            actual.append('GENERATE_DN')
        elif dispatch_type == '無須補貨':
            actual.append('NO_REPLENISH')
        elif dispatch_type == 'D001':
            actual.append('D001')
        elif dispatch_type == 'Buyer需要訂貨':
            actual.append('BUYER_ORDER')
        else:
            actual.append(str(dispatch_type))
    
    for i, (exp, act) in enumerate(zip(expected, actual)):
        status = "PASS" if exp == act else "FAIL"
        print(f"Row {i+1}: Expected={exp}, Actual={act}, Status={status}")

if __name__ == "__main__":
    test_updated_dispatch_logic()