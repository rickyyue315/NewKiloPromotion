import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def test_simple_check():
    """簡單檢查邏輯問題"""
    
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
    print("Simple Check:")
    print("=" * 80)
    
    problem_found = False
    
    for _, row in detail.iterrows():
        site = row['Site']
        rp_type = row['RP_Type']
        supply_source = row['Supply_source']
        suggested_dn_qty = row['Suggested_DN_Qty']
        dispatch_type = row['Dispatch_Type']
        
        print(f"Site: {site}, RP: {rp_type}, Supply: {supply_source}")
        print(f"  Suggested_DN_Qty: {suggested_dn_qty}")
        print(f"  Dispatch_Type: {dispatch_type}")
        
        # 檢查邏輯
        if rp_type == 'ND' and suggested_dn_qty == 0:
            # 應該顯示 "無須補貨"
            if '需生成' in str(dispatch_type) or '開PO' in str(dispatch_type):
                print(f"  [PROBLEM] Suggested_DN_Qty=0 but Dispatch_Type shows action needed")
                problem_found = True
            else:
                print(f"  [OK] Suggested_DN_Qty=0 and Dispatch_Type is correct")
        print()
    
    if problem_found:
        print("ISSUE CONFIRMED: Found ND sites with Suggested_DN_Qty=0 but incorrect Dispatch_Type")
    else:
        print("NO ISSUE: All ND sites with Suggested_DN_Qty=0 have correct Dispatch_Type")

if __name__ == "__main__":
    test_simple_check()