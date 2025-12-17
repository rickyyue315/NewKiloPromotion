import pandas as pd
from promo_calculator import Config, calculate_demand

def test_dn_qty_zero_logic():
    """測試 Suggested_DN_Qty 為 0 時的 Dispatch_Type 邏輯"""
    
    # 創建測試數據
    test_data = pd.DataFrame({
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'RP_Type': ['ND', 'ND', 'ND', 'ND'],
        'Supply_source': [1, 2, 4, 2],
        'SaSa_Net_Stock': [50, 30, 20, 10],
        'Pending_Received': [0, 0, 0, 0],
        'Safety_Stock': [5, 5, 5, 5],
        'Last_Month_Sold_Qty_capped': [0, 0, 0, 0],
        'Daily_Sales_Rate': [0, 0, 0, 0],
        'Promo_Target_Cover_Days': [7, 7, 7, 7],  # 添加缺少的欄位
        'Base_Demand': [0, 0, 0, 0],
        'Site_Promo_Demand': [0, 0, 0, 0],  # 全部設為 0，應該導致 Suggested_DN_Qty = 0
        'Total_Demand': [0, 0, 0, 0],
        'Net_Demand_raw': [0, 0, 0, 0],
        'Net_Demand_for_Dispatch': [0, 0, 0, 0],
        'MOQ': [10, 10, 10, 10],
        'Promotion_Days': [5, 5, 5, 5],
        'Suggested_Dispatch_Qty': [0, 0, 0, 0],
        'Suggested_DN_Qty': [0, 0, 0, 0],  # 全部設為 0
    })
    
    config = Config()
    
    # 計算 Dispatch_Type
    result_df = calculate_demand(test_data, config)
    
    # 檢查結果
    print("測試結果:")
    for _, row in result_df.iterrows():
        print(f"Site: {row['Site']}, Suggested_DN_Qty: {row['Suggested_DN_Qty']}, Dispatch_Type: {row['Dispatch_Type']}")
        
        # 驗證邏輯：當 Suggested_DN_Qty = 0 時，ND 站點應該顯示 '無須補貨'
        if row['RP_Type'] == 'ND' and row['Suggested_DN_Qty'] == 0:
            expected_type = '無須補貨'
            if row['Dispatch_Type'] != expected_type:
                print(f"❌ 錯誤: Site {row['Site']} 的 Suggested_DN_Qty 為 0，但 Dispatch_Type 顯示為 '{row['Dispatch_Type']}'，應該是 '{expected_type}'")
            else:
                print(f"✅ 正確: Site {row['Site']} 的 Suggested_DN_Qty 為 0，Dispatch_Type 正確顯示為 '{row['Dispatch_Type']}'")
    
    # 測試另一種情況：Suggested_DN_Qty > 0
    test_data_positive = test_data.copy()
    test_data_positive.loc[0, 'Site_Promo_Demand'] = 20  # 設置為 > 0
    test_data_positive.loc[0, 'Total_Demand'] = 20
    test_data_positive.loc[0, 'Suggested_Dispatch_Qty'] = 20
    test_data_positive.loc[0, 'Suggested_DN_Qty'] = 20  # 設置為 > 0
    
    result_df_positive = calculate_demand(test_data_positive, config)
    
    print("\n測試 Suggested_DN_Qty > 0 的情況:")
    for _, row in result_df_positive.iterrows():
        print(f"Site: {row['Site']}, Suggested_DN_Qty: {row['Suggested_DN_Qty']}, Dispatch_Type: {row['Dispatch_Type']}")
        
        # 驗證邏輯：當 Suggested_DN_Qty > 0 時，ND 站點應該根據 Supply_source 顯示不同的類型
        if row['RP_Type'] == 'ND' and row['Suggested_DN_Qty'] > 0:
            supply_source = int(row['Supply_source'])
            if supply_source == 1:
                expected_type = '開PO'
            elif supply_source == 2:
                expected_type = '需生成 DN'
            elif supply_source == 4:
                expected_type = '開PO'
            else:
                expected_type = 'ND'
                
            if row['Dispatch_Type'] != expected_type:
                print(f"❌ 錯誤: Site {row['Site']} 的 Supply_source 為 {supply_source}，但 Dispatch_Type 顯示為 '{row['Dispatch_Type']}'，應該是 '{expected_type}'")
            else:
                print(f"✅ 正確: Site {row['Site']} 的 Supply_source 為 {supply_source}，Dispatch_Type 正確顯示為 '{row['Dispatch_Type']}'")

if __name__ == "__main__":
    test_dn_qty_zero_logic()