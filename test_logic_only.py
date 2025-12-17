import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def test_logic_only():
    """只檢查邏輯，不打印中文字符"""
    
    config = Config()
    
    # 創建模擬的 File A 數據
    file_a_data = {
        'Article': ['TEST001', 'TEST002'],
        'Site': ['ND001', 'ND002'],
        'RP Type': ['ND', 'ND'],
        'Supply source': [2, 2],
        'SaSa Net Stock': [50, 30],
        'Pending Received': [0, 0],
        'Safety Stock': [5, 5],
        'Last Month Sold Qty': [0, 0],
        'MOQ': [10, 10],
    }
    
    # 創建模擬的 File B Sheet1 數據
    file_b1_data = {
        'Group No.': ['G001', 'G002'],
        'Article': ['TEST001', 'TEST002'],
        'SKU Target': [0, 100],  # 一個為 0，一個為 100
        'Target Type': ['ALL', 'ALL'],
        'Promotion Days': [5, 5],
    }
    
    # 創建模擬的 File B Sheet2 數據
    file_b2_data = {
        'Site': ['ND001', 'ND002'],
        'Shop Target(HK)': [0, 0],
        'Shop Target(MO)': [0, 0],
        'Shop Target(ALL)': [0, 0],
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
    print("Logic Only Check:")
    print("=" * 80)
    
    problem_count = 0
    total_nd_zero = 0
    
    for _, row in detail.iterrows():
        site = row['Site']
        rp_type = row['RP_Type']
        supply_source = row['Supply_source']
        suggested_dn_qty = row['Suggested_DN_Qty']
        dispatch_type = row['Dispatch_Type']
        
        print(f"Site: {site}, RP: {rp_type}, Supply: {supply_source}")
        print(f"  Suggested_DN_Qty: {suggested_dn_qty}")
        print(f"  Dispatch_Type length: {len(str(dispatch_type))}")
        
        # 檢查邏輯
        if rp_type == 'ND' and suggested_dn_qty == 0:
            total_nd_zero += 1
            # 檢查 Dispatch_Type 是否包含中文字符（長度 > 10 可能表示包含中文）
            if len(str(dispatch_type)) > 10:
                print(f"  [PROBLEM] Dispatch_Type might be showing action instead of 'No replenishment'")
                problem_count += 1
            else:
                print(f"  [OK] Dispatch_Type seems correct")
        print()
    
    print(f"Summary:")
    print(f"  Total ND sites with Suggested_DN_Qty=0: {total_nd_zero}")
    print(f"  Problems found: {problem_count}")
    
    if problem_count > 0:
        print("  ISSUE CONFIRMED: Some ND sites with Suggested_DN_Qty=0 show incorrect Dispatch_Type")
        return False
    else:
        print("  NO ISSUE: All ND sites with Suggested_DN_Qty=0 have correct Dispatch_Type")
        return True

if __name__ == "__main__":
    test_logic_only()