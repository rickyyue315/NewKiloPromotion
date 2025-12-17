import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def test_comprehensive():
    """全面測試 Dispatch_Type 邏輯"""
    
    config = Config()
    
    # 創建模擬的 File A 數據 - 包含多種情況
    file_a_data = {
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004', 'ND005'],
        'RP Type': ['ND', 'ND', 'ND', 'ND', 'ND'],
        'Supply source': [2, 2, 1, 4, 2],
        'SaSa Net Stock': [50, 30, 20, 10, 40],
        'Pending Received': [0, 0, 0, 0, 0],
        'Safety Stock': [5, 5, 5, 5, 5],
        'Last Month Sold Qty': [0, 0, 0, 0, 0],
        'MOQ': [10, 10, 10, 10, 10],
    }
    
    # 創建模擬的 File B Sheet1 數據
    file_b1_data = {
        'Group No.': ['G001', 'G002', 'G003', 'G004', 'G005'],
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005'],
        'SKU Target': [0, 0, 100, 100, 50],  # 不同的目標
        'Target Type': ['ALL', 'ALL', 'ALL', 'ALL', 'ALL'],
        'Promotion Days': [5, 5, 5, 5, 5],
    }
    
    # 創建模擬的 File B Sheet2 數據
    file_b2_data = {
        'Site': ['ND001', 'ND002', 'ND003', 'ND004', 'ND005'],
        'Shop Target(HK)': [0, 0, 0, 0, 0],
        'Shop Target(MO)': [0, 0, 0, 0, 0],
        'Shop Target(ALL)': [0, 0, 0, 0, 0],
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
    print("Comprehensive Test:")
    print("=" * 80)
    
    problem_count = 0
    
    for _, row in detail.iterrows():
        site = row['Site']
        rp_type = row['RP_Type']
        supply_source = row['Supply_source']
        suggested_dn_qty = row['Suggested_DN_Qty']
        dispatch_type = row['Dispatch_Type']
        site_promo_demand = row['Site_Promo_Demand']
        
        print(f"Site: {site}, RP: {rp_type}, Supply: {supply_source}")
        print(f"  Site_Promo_Demand: {site_promo_demand}")
        print(f"  Suggested_DN_Qty: {suggested_dn_qty}")
        print(f"  Dispatch_Type length: {len(str(dispatch_type))}")
        
        # 檢查邏輯
        if rp_type == 'ND':
            if suggested_dn_qty == 0:
                # 應該顯示 "無須補貨"
                if len(str(dispatch_type)) > 10:  # 如果長度 > 10，可能顯示了其他內容
                    print(f"  [PROBLEM] Suggested_DN_Qty=0 but Dispatch_Type seems wrong")
                    problem_count += 1
                else:
                    print(f"  [OK] Suggested_DN_Qty=0 and Dispatch_Type seems correct")
            else:
                # Suggested_DN_Qty > 0，應該根據 Supply_source 顯示不同類型
                expected_type = ""
                if supply_source == 2:
                    expected_type = "需生成 DN"
                elif supply_source in (1, 4):
                    expected_type = "開PO"
                
                # 檢查是否包含預期的關鍵字
                if expected_type and expected_type not in str(dispatch_type):
                    print(f"  [PROBLEM] Expected to contain '{expected_type}' but got different")
                    problem_count += 1
                else:
                    print(f"  [OK] Suggested_DN_Qty>0 and Dispatch_Type seems correct")
        print()
    
    print(f"Summary:")
    print(f"  Problems found: {problem_count}")
    
    if problem_count > 0:
        print("  ISSUE CONFIRMED: Found Dispatch_Type logic problems")
        return False
    else:
        print("  NO ISSUE: All Dispatch_Type logic seems correct")
        return True

if __name__ == "__main__":
    test_comprehensive()