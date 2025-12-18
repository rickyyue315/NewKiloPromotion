import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def test_hb87_rf_logic():
    """Test HB87-RF special logic"""
    
    config = Config()
    
    # Create mock File A data - test HB87-RF logic
    file_a_data = {
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'Site': ['HB87', 'HB87', 'RF001', 'RF002'],
        'RP Type': ['RF', 'RF', 'RF', 'RF'],
        'Supply source': [2, 2, 2, 2],
        'SaSa Net Stock': [10, 20, 30, 40],
        'Pending Received': [5, 10, 0, 0],
        'Safety Stock': [50, 60, 70, 80],
        'Last Month Sold Qty': [0, 0, 0, 0],
        'MOQ': [12, 12, 12, 12],
    }
    
    # Create mock File B Sheet1 data
    file_b1_data = {
        'Group No.': ['G001', 'G002', 'G003', 'G004'],
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'SKU Target': [0, 100, 0, 100],  # TEST001 and TEST003 have no Target, TEST002 and TEST004 have Target
        'Target Type': ['ALL', 'ALL', 'ALL', 'ALL'],
        'Promotion Days': [5, 5, 5, 5],
    }
    
    # Create mock File B Sheet2 data
    file_b2_data = {
        'Site': ['HB87', 'HB87', 'RF001', 'RF002'],
        'Shop Target(HK)': [0, 0, 0, 0],
        'Shop Target(MO)': [0, 0, 0, 0],
        'Shop Target(ALL)': [0, 0, 0, 0],
    }
    
    # Convert to DataFrame
    df_a_raw = pd.DataFrame(file_a_data)
    df_b1_raw = pd.DataFrame(file_b1_data)
    df_b2_raw = pd.DataFrame(file_b2_data)
    
    # Process data
    df_a_clean, warn_a = prepare_file_a(df_a_raw, config)
    df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, config)
    merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, config)
    detail = calculate_demand(merged, config, lead_time=7)
    
    # Check results
    print("Testing HB87-RF Logic:")
    print("=" * 80)
    
    for _, row in detail.iterrows():
        site = row['Site']
        rp_type = row['RP_Type']
        safety_stock = row['Safety_Stock']
        sasa_net_stock = row['SaSa_Net_Stock']
        pending_received = row['Pending_Received']
        moq = row['MOQ']
        site_promo_demand = row['Site_Promo_Demand']
        suggested_dispatch_qty = row['Suggested_Dispatch_Qty']
        dispatch_remark = row['Dispatch_Remark']
        
        print(f"Site: {site}, RP: {rp_type}")
        print(f"  Safety Stock: {safety_stock}, SaSa Net Stock: {sasa_net_stock}, Pending Received: {pending_received}")
        print(f"  MOQ: {moq}")
        print(f"  Site_Promo_Demand: {site_promo_demand}")
        print(f"  Suggested_Dispatch_Qty: {suggested_dispatch_qty}")
        print(f"  Dispatch_Remark: {dispatch_remark}")
        
        # 計算期望值（用於驗證）
        if site == "HB87" and rp_type == "RF" and site_promo_demand <= 0:
            expected_raw = safety_stock - sasa_net_stock - pending_received
            if expected_raw > 0 and moq > 0:
                expected_result = round(expected_raw / moq) * moq
                expected_result = max(expected_result, moq)
                print(f"  Expected calculation: Safety({safety_stock}) - Net({sasa_net_stock}) - Pending({pending_received}) = {expected_raw}")
                print(f"  Expected result: round({expected_raw}/{moq})*{moq} = {expected_result}")
                
                if suggested_dispatch_qty == expected_result:
                    print(f"  [CORRECT] Suggested_Dispatch_Qty matches expected calculation")
                else:
                    print(f"  [ERROR] Expected {expected_result} but got {suggested_dispatch_qty}")
            
            if dispatch_remark == "HB87-RF派貨":
                print(f"  [CORRECT] Dispatch_Remark shows 'HB87-RF派貨'")
            else:
                print(f"  [ERROR] Expected 'HB87-RF派貨' but got '{dispatch_remark}'")
        
        print()
    
    # Special check for HB87-RF cases
    hb87_rf_cases = detail[
        (detail['Site'] == 'HB87') & 
        (detail['RP_Type'] == 'RF') & 
        (detail['Site_Promo_Demand'] <= 0)
    ]
    
    print("=== HB87-RF Special Logic Verification ===")
    if not hb87_rf_cases.empty:
        for _, row in hb87_rf_cases.iterrows():
            safety_stock = row['Safety_Stock']
            sasa_net_stock = row['SaSa_Net_Stock']
            pending_received = row['Pending_Received']
            moq = row['MOQ']
            suggested_dispatch_qty = row['Suggested_Dispatch_Qty']
            dispatch_remark = row['Dispatch_Remark']
            
            # 手動計算期望值
            raw_value = safety_stock - sasa_net_stock - pending_received
            if raw_value > 0 and moq > 0:
                expected_qty = round(raw_value / moq) * moq
                expected_qty = max(expected_qty, moq)
                
                print(f"HB87-RF Case:")
                print(f"  Formula: Mround(({safety_stock}-{sasa_net_stock}-{pending_received}), {moq})")
                print(f"  Raw value: {raw_value}")
                print(f"  Expected: {expected_qty}")
                print(f"  Actual: {suggested_dispatch_qty}")
                print(f"  Remark: {dispatch_remark}")
                
                if suggested_dispatch_qty == expected_qty and dispatch_remark == "HB87-RF派貨":
                    print(f"  [SUCCESS] HB87-RF logic working correctly!")
                else:
                    print(f"  [FAILED] HB87-RF logic has issues")
                print()
    else:
        print("No HB87-RF cases found for testing")
    
    # Check other RF sites are not affected
    other_rf_cases = detail[
        (detail['Site'] != 'HB87') & 
        (detail['RP_Type'] == 'RF')
    ]
    
    print("=== Other RF Sites (should not be affected) ===")
    for _, row in other_rf_cases.iterrows():
        site = row['Site']
        suggested_dispatch_qty = row['Suggested_Dispatch_Qty']
        dispatch_remark = row['Dispatch_Remark']
        site_promo_demand = row['Site_Promo_Demand']
        
        print(f"Site: {site}")
        print(f"  Site_Promo_Demand: {site_promo_demand}")
        print(f"  Suggested_Dispatch_Qty: {suggested_dispatch_qty}")
        print(f"  Dispatch_Remark: {dispatch_remark}")
        
        # These sites should not have "HB87-RF派貨" remark
        if dispatch_remark == "HB87-RF派貨":
            print(f"  [ERROR] Non-HB87 site should not have 'HB87-RF派貨' remark")
        else:
            print(f"  [CORRECT] Non-HB87 site does not have HB87-RF remark")
        print()

if __name__ == "__main__":
    test_hb87_rf_logic()