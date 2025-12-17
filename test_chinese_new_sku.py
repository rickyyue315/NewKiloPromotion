#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新SKU中文提示功能
"""

import pandas as pd
import sys
import os
from pathlib import Path

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from promo_calculator import (
    Config,
    prepare_file_a,
    prepare_file_b,
    calculate_demand,
    generate_summary,
    export_to_excel
)

def create_test_file_a():
    """創建測試用的 File A"""
    data = {
        Config.COL_A_ARTICLE: ["NEW001", "NEW002", "REG001"],
        Config.COL_A_SITE: ["HK01", "HK01", "HK01"],
        Config.COL_A_SUPPLY_SOURCE: [1, 2, 3],  # Use valid supply source values
        Config.COL_A_LAST_MONTH_SOLD: [50, 30, 20],  # Increase to generate demand
        Config.COL_A_LAUNCH_DATE: ["", "", "2023-01-01"],  # 新SKU沒有Launch Date
        Config.COL_A_RP_TYPE: ["RF", "RF", "RF"],
        Config.COL_A_NET_STOCK: [10, 5, 100],  # Lower stock for new SKUs to trigger dispatch
        Config.COL_A_PENDING: [0, 0, 0],
        Config.COL_A_SAFETY: [10, 10, 10],
        Config.COL_A_MOQ: [5, 5, 5]
    }
    df = pd.DataFrame(data)
    return df

def create_test_file_b():
    """創建測試用的 File B"""
    # Sheet 1
    b1_data = {
        Config.COL_B1_ARTICLE: ["NEW001", "NEW002", "REG001"],
        Config.COL_B1_GROUP_NO: ["G001", "G002", "G003"],
        Config.COL_B1_SKU_TARGET: [100, 100, 100],
        Config.COL_B1_TARGET_TYPE: ["ALL", "ALL", "ALL"]
    }
    df_b1 = pd.DataFrame(b1_data)
    
    # Sheet 2
    b2_data = {
        Config.COL_B2_SITE: ["HK01"],
        Config.COL_B2_HK: [0.3],
        Config.COL_B2_MO: [0.3],
        Config.COL_B2_ALL: [0.4]
    }
    df_b2 = pd.DataFrame(b2_data)
    
    return df_b1, df_b2

def test_chinese_new_sku_logic():
    """Test Chinese New SKU alert logic"""
    print("=" * 60)
    print("Testing Chinese New SKU alert functionality")
    print("=" * 60)
    
    # 創建配置
    config = Config()
    
    # 創建測試數據
    df_a = create_test_file_a()
    df_b1, df_b2 = create_test_file_b()
    
    # 處理數據
    df_a_processed, warnings_a = prepare_file_a(df_a, config)
    df_b1_processed, df_b2_processed, warnings_b = prepare_file_b(df_b1, df_b2, config)
    
    print("\nProcessed File A data:")
    print(df_a_processed[["Article", "Launch_Date"]].to_string())
    
    # 合併數據並計算需求
    from promo_calculator import merge_data
    merged_df, merge_warnings = merge_data(df_a_processed, df_b1_processed, df_b2_processed, config)
    detail_df = calculate_demand(merged_df, config)
    
    # Test determine_dispatch_type function
    print("\nTesting determine_dispatch_type function:")
    for _, row in detail_df.iterrows():
        article = row["Article"]
        launch_date = row["Launch_Date"]
        dn_qty = row["Suggested_DN_Qty"]
        
        # Check if it's a new SKU
        is_new_sku = (launch_date == "" and dn_qty > 0)
        
        dispatch_type = row["Dispatch_Type"]
        
        print(f"Article: {article}")
        print(f"  Launch Date: '{launch_date}' (blank means new SKU)")
        print(f"  Suggested DN Qty: {dn_qty}")
        print(f"  Is New SKU: {is_new_sku}")
        # Handle potential encoding issues with Chinese characters
        try:
            print(f"  Dispatch Type: {dispatch_type}")
        except UnicodeEncodeError:
            print(f"  Dispatch Type: [Contains Chinese characters - New SKU alert triggered]")
        print()
    
    # Test generate_summary function
    print("\nTesting generate_summary function:")
    summary_df = generate_summary(detail_df, config)
    
    # Check for New SKU alerts
    new_sku_alerts = summary_df[summary_df["New_SKU_Alert"] != ""]
    
    if not new_sku_alerts.empty:
        print("\nFound New SKU alerts:")
        try:
            print(new_sku_alerts[["Article", "New_SKU_Alert", "Enhanced_Inventory_Status"]].to_string())
        except UnicodeEncodeError:
            print("[DataFrame contains Chinese characters - showing individual rows]")
            for _, row in new_sku_alerts.iterrows():
                print(f"Article: {row['Article']}")
                print(f"  New_SKU_Alert: [Contains Chinese characters]")
                print(f"  Enhanced_Inventory_Status: [Contains Chinese characters]")
        
        # Check if Enhanced_Inventory_Status contains Chinese alert
        for _, row in new_sku_alerts.iterrows():
            enhanced_status = row["Enhanced_Inventory_Status"]
            if "新SKU必須由Buyer首次派貨" in enhanced_status:
                print(f"\n[OK] Article {row['Article']} Enhanced_Inventory_Status contains Chinese alert:")
                try:
                    print(f"  {enhanced_status}")
                except UnicodeEncodeError:
                    print(f"  [Contains Chinese characters - New SKU alert is present]")
            else:
                print(f"\n[FAIL] Article {row['Article']} Enhanced_Inventory_Status missing Chinese alert")
    else:
        print("\nNo New SKU alerts found")
    
    # Test export functionality
    print("\nTesting export functionality:")
    output_file = Path("test_chinese_new_sku_output.xlsx")
    export_to_excel(detail_df, summary_df, df_a_processed, df_b1_processed, df_b2_processed, output_file)
    print(f"Results exported to: {output_file}")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    test_chinese_new_sku_logic()