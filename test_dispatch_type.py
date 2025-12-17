import pandas as pd
import numpy as np
from promo_calculator import Config, calculate_demand

def test_dispatch_type_logic():
    """測試 ND 站點的 Dispatch_Type 邏輯"""
    
    # 創建測試數據
    test_data = pd.DataFrame({
        'Article': ['TEST001', 'TEST002', 'TEST003', 'TEST004'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'RP_Type': ['ND', 'ND', 'ND', 'ND'],
        'SaSa_Net_Stock': [50, 30, 20, 10],
        'Pending_Received': [0, 0, 0, 0],
        'Safety_Stock': [10, 10, 10, 10],
        'Last_Month_Sold_Qty_capped': [100, 80, 60, 40],
        'MOQ': [12, 12, 12, 12],
        'Supply_source': [1, 2, 4, 2],  # 不同的供應源
        'SKU_Target': [100, 80, 60, 40],
        'Site_Target_%': [0.5, 0.5, 0.5, 0.5],
        'Is_Promo_SKU': [True, True, True, True],
        'Promo_Target_Cover_Days': [7, 7, 7, 7],  # 添加缺少的欄位
        'Promotion_Days': [5, 3, 6, 2],  # 不同的推廣天數
    })
    
    # 計算需求
    cfg = Config()
    result = calculate_demand(test_data, cfg)
    
    print("=== Test ND Site Dispatch_Type Logic ===")
    print("Site\tSupply_source\tSuggested_DN_Qty\tDispatch_Type\tDispatch_Remark")
    print("-" * 80)
    
    for _, row in result.iterrows():
        print(f"{row['Site']}\t{row['Supply_source']}\t\t{row['Suggested_DN_Qty']}\t\t{row['Dispatch_Type']}\t\t{row['Dispatch_Remark']}")
    
    print("\n=== Expected Results ===")
    print("ND001: Supply_source=1, Suggested_DN_Qty>0 -> Dispatch_Type=開PO")
    print("ND002: Supply_source=2, Suggested_DN_Qty>0 -> Dispatch_Type=開DN")
    print("ND003: Supply_source=4, Suggested_DN_Qty>0 -> Dispatch_Type=開PO")
    print("ND004: Supply_source=2, Suggested_DN_Qty>0 -> Dispatch_Type=開DN")
    print("\nAll ND sites should have Dispatch_Remark='ND 派貨'")

if __name__ == "__main__":
    test_dispatch_type_logic()