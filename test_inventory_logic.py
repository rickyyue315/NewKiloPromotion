#!/usr/bin/env python3
"""
測試新的庫存狀態邏輯
"""

import pandas as pd
import numpy as np
from pathlib import Path
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand, generate_summary

def create_test_data():
    """創建測試數據"""
    # 創建測試用的 File A 數據
    test_data_a = {
        'Article': ['ART001', 'ART001', 'ART001', 'ART002', 'ART002', 'ART002'],
        'Site': ['D001', 'H001', 'H002', 'D001', 'H003', 'S001'],
        'RP Type': ['RF', 'RF', 'RF', 'RF', 'RF', 'RF'],
        'SaSa Net Stock': [150, 50, 30, 80, 20, 40],
        'Pending Received': [10, 5, 3, 8, 2, 4],
        'Safety Stock': [20, 10, 10, 15, 5, 8],
        'Last Month Sold Qty': [100, 50, 30, 80, 20, 40],
        'MOQ': [10, 10, 10, 10, 10, 10],
        'Supply source': [2, 2, 2, 1, 1, 4],
        'In Quality Insp': [0, 0, 0, 0, 0, 0],
        'Blocked': [0, 0, 0, 0, 0, 0]
    }
    
    # 創建測試用的 File B Sheet1 數據
    test_data_b1 = {
        'Group No.': ['G001', 'G002'],
        'Article': ['ART001', 'ART002'],
        'SKU Target': [200, 100],
        'Target Type': ['ALL', 'ALL'],
        'Target Cover Days': [7, 7]
    }
    
    # 創建測試用的 File B Sheet2 數據
    test_data_b2 = {
        'Site': ['H001', 'H002', 'H003', 'S001'],
        'Shop Target(HK)': [0.5, 0.5, 0.5, 0.5],
        'Shop Target(MO)': [0.3, 0.3, 0.3, 0.3],
        'Shop Target(ALL)': [1.0, 1.0, 1.0, 1.0]
    }
    
    return pd.DataFrame(test_data_a), pd.DataFrame(test_data_b1), pd.DataFrame(test_data_b2)

def test_inventory_logic():
    """測試庫存邏輯"""
    print("=== Testing New Inventory Logic ===\n")
    
    # 創建測試數據
    df_a, df_b1, df_b2 = create_test_data()
    
    # 初始化配置
    cfg = Config()
    
    # 準備數據
    df_a_clean, warn_a = prepare_file_a(df_a, cfg)
    df_b1_clean, df_b2_clean, warn_b = prepare_file_b(df_b1, df_b2, cfg)
    
    # 合併數據
    merged, warn_merge = merge_data(df_a_clean, df_b1_clean, df_b2_clean, cfg)
    
    # 計算需求
    detail = calculate_demand(merged, cfg, lead_time=7)
    
    # 生成摘要報告
    summary = generate_summary(detail, cfg)
    
    # 顯示測試結果
    print("Test Data Summary:")
    print(f"- ART001 (Supply source=2): D001 stock=150, H-site stock=80, H-site pending=8")
    print(f"- ART002 (Supply source=1): D001 stock=80, H-site stock=20, H-site pending=2")
    print()
    
    print("Generated Summary Report:")
    display_cols = [
        'Group_No', 'Article', 'Total_Demand', 'D001_SaSa_Net_Stock', 
        'Effective_Inventory', 'Enhanced_Inventory_Status', 'Out_of_Stock_Warning'
    ]
    
    for col in display_cols:
        if col in summary.columns:
            if col == 'Enhanced_Inventory_Status':
                # Handle the Chinese characters in status
                values = list(summary[col])
                print(f"- {col}: {values}")
            else:
                print(f"- {col}: {list(summary[col])}")
    
    print("\nLogic Verification:")
    
    # 驗證 ART001 (Supply source=2)
    art001_row = summary[summary['Article'] == 'ART001'].iloc[0]
    art001_effective = art001_row['Effective_Inventory']
    art001_status = art001_row['Enhanced_Inventory_Status']
    art001_demand = art001_row['Total_Demand']
    art001_d001_stock = art001_row['D001_SaSa_Net_Stock']
    
    print(f"\nART001 Verification:")
    print(f"- Effective inventory calculation: D001(150) + H-site stock(80) + H-site pending(8) = {art001_effective}")
    print(f"- Total demand: {art001_demand}")
    print(f"- D001 stock: {art001_d001_stock}")
    expected_status = "Sufficient stock, RP team will arrange Lot For Lot" if art001_demand > art001_effective and art001_d001_stock > 100 else "Other"
    print(f"- Expected status: {expected_status}")
    print(f"- Actual status: {art001_status}")
    
    # 驗證 ART002 (Supply source=1)
    art002_row = summary[summary['Article'] == 'ART002'].iloc[0]
    art002_effective = art002_row['Effective_Inventory']
    art002_status = art002_row['Enhanced_Inventory_Status']
    art002_demand = art002_row['Total_Demand']
    
    print(f"\nART002 Verification:")
    print(f"- Effective inventory calculation: D001(80) + H-site stock(20) + H-site pending(2) = {art002_effective}")
    print(f"- Total demand: {art002_demand}")
    expected_status = "Sufficient stock" if art002_demand > art002_effective else "Insufficient stock, Buyer needs to open PO"
    print(f"- Expected status: {expected_status}")
    print(f"- Actual status: {art002_status}")
    
    print("\n=== Test Complete ===")
    
    return summary

if __name__ == "__main__":
    test_inventory_logic()