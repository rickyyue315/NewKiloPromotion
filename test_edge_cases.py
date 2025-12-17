import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def test_edge_cases():
    """測試邊界情況"""
    
    config = Config()
    
    # 創建模擬的 File A 數據 - 測試邊界情況
    file_a_data = {
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'RP Type': ['ND', 'ND', 'ND', 'ND'],
        'Supply source': [2, 2, 2, 2],
        'SaSa Net Stock': [50, 30, 20, 10],
        'Pending Received': [0, 0, 0, 0],
        'Safety Stock': [5, 5, 5, 5],
        'Last Month Sold Qty': [0, 0, 0, 0],
        'MOQ': [10, 10, 10, 10],
    }
    
    # 創建模擬的 File B Sheet1 數據 - 測試邊界情況
    file_b1_data = {
        'Group No.': ['G001', 'G002', 'G003', 'G004'],
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'SKU Target': [0, 0.1, 0.5, 1],  # 測試非常小的數值
        'Target Type': ['ALL', 'ALL', 'ALL', 'ALL'],
        'Promotion Days': [5, 5, 5, 5],
    }
    
    # 創建模擬的 File B Sheet2 數據
    file_b2_data = {
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'Shop Target(HK)': [0, 0, 0, 0],
        'Shop Target(MO)': [0, 0, 0, 0],
        'Shop Target(ALL)': [0, 0, 0, 0],
    }
    
    # 轉換為 DataFrame
    df_a_raw = pd.DataFrame(file_a_data)
    df_b1_raw = pd.DataFrame(file_b1_data)
    df_b2_raw = pd.DataFrame(file_b2_data)
    
    # 處理數據
    df_a_clean, warn_a = prepare_file_a(df_a_raw, config)
    df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, config)
    merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, config)
    detail = calculate_demand(merged, config, lead_time=7)
    
    # 檢查結果
    print("Edge Cases Test:")
    print("=" * 80)
    
    for _, row in detail.iterrows():
        site = row['Site']
        rp_type = row['RP_Type']
        supply_source = row['Supply_source']
        suggested_dn_qty = row['Suggested_DN_Qty']
        dispatch_type = row['Dispatch_Type']
        site_promo_demand = row['Site_Promo_Demand']
        sku_target = row['SKU_Target']
        site_target_pct = row['Site_Target_%']
        
        print(f"Site: {site}, RP: {rp_type}, Supply: {supply_source}")
        print(f"  SKU_Target: {sku_target}, Site_Target_%: {site_target_pct}")
        print(f"  Site_Promo_Demand: {site_promo_demand}")
        print(f"  Suggested_DN_Qty: {suggested_dn_qty}")
        print(f"  Dispatch_Type length: {len(str(dispatch_type))}")
        
        # 檢查邏輯
        if rp_type == 'ND':
            if suggested_dn_qty == 0:
                # 應該顯示 "無須補貨"
                if len(str(dispatch_type)) > 10:  # 如果長度 > 10，可能顯示了其他內容
                    print(f"  [PROBLEM] Suggested_DN_Qty=0 but Dispatch_Type seems wrong")
                else:
                    print(f"  [OK] Suggested_DN_Qty=0 and Dispatch_Type seems correct")
            else:
                print(f"  [INFO] Suggested_DN_Qty > 0, checking Dispatch_Type logic")
        print()
    
    # 檢查是否有任何異常情況
    print("Checking for potential issues:")
    problem_cases = detail[
        (detail['RP_Type'] == 'ND') & 
        (detail['Suggested_DN_Qty'] == 0)
    ]
    
    if not problem_cases.empty:
        print(f"Found {len(problem_cases)} ND sites with Suggested_DN_Qty=0")
        for _, row in problem_cases.iterrows():
            print(f"  Site: {row['Site']}, Dispatch_Type: '{row['Dispatch_Type']}'")
            print(f"  Site_Promo_Demand: {row['Site_Promo_Demand']}")
            print(f"  SKU_Target: {row['SKU_Target']}, Site_Target_%: {row['Site_Target_%']}")
    else:
        print("No ND sites with Suggested_DN_Qty=0 found")

if __name__ == "__main__":
    test_edge_cases()