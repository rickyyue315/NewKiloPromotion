#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test New SKU Logic Fix
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import promo_calculator
sys.path.append(str(Path(__file__).parent))

from promo_calculator import (
    Config,
    prepare_file_a,
    prepare_file_b,
    merge_data,
    calculate_demand,
    generate_summary,
    export_to_excel
)


def create_test_data():
    """Create test data"""
    # Create test File A data
    test_data_a = {
        "Article": ["NEW001", "REG001", "NEW002"],
        "Site": ["HA1", "HA1", "HB1"],
        "RP Type": ["RF", "RF", "ND"],
        "SaSa Net Stock": [10, 50, 20],
        "Pending Received": [5, 10, 0],
        "Safety Stock": [5, 15, 10],
        "Last Month Sold Qty": [20, 100, 30],
        "MOQ": [10, 20, 5],
        "Supply source": [2, 1, 2],
        "Launch Date": ["", "2023-01-01", None],  # NEW001 and NEW002 have blank Launch Date
        "In Quality Insp.": [0, 0, 0],
        "Blocked": [0, 0, 0]
    }
    
    # Create test File B Sheet1 data
    test_data_b1 = {
        "Group No.": ["G001", "G001", "G002"],
        "Article": ["NEW001", "REG001", "NEW002"],
        "SKU Target": [100, 200, 150],
        "Target Type": ["ALL", "ALL", "HK"],
        "Promotion Days": [7, 5, 10],
        "Target Cover Days": [7, 7, 7]
    }
    
    # Create test File B Sheet2 data
    test_data_b2 = {
        "Site": ["HA1", "HB1", "D001"],
        "Shop Target(HK)": [0.3, 0.4, 0],
        "Shop Target(MO)": [0.3, 0.3, 0],
        "Shop Target(ALL)": [0.4, 0.3, 1]
    }
    
    return pd.DataFrame(test_data_a), pd.DataFrame(test_data_b1), pd.DataFrame(test_data_b2)


def test_new_sku_logic():
    """Test new SKU logic"""
    print("=== Testing New SKU Logic ===")
    
    # Create test data
    df_a_raw, df_b1_raw, df_b2_raw = create_test_data()
    
    # Save test data to temporary files
    df_a_raw.to_excel("test_file_a.xlsx", index=False, sheet_name="Sheet1")
    with pd.ExcelWriter("test_file_b.xlsx") as writer:
        df_b1_raw.to_excel(writer, sheet_name="Sheet 1", index=False)
        df_b2_raw.to_excel(writer, sheet_name="Sheet 2", index=False)
    
    try:
        # Read and process data
        cfg = Config()
        df_a_clean, warn_a = prepare_file_a(df_a_raw, cfg)
        df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, cfg)
        
        print("File A prepared, warnings:", warn_a)
        print("File B prepared, warnings:", warn_b)
        
        # Check Launch Date processing
        print("\n=== Checking Launch Date Processing ===")
        print("Launch_Date field values:")
        for idx, row in df_a_clean.iterrows():
            print(f"  {row['Article']}: '{row.get('Launch_Date', 'N/A')}'")
        
        # Merge data
        merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, cfg)
        print("\nMerge completed, warnings:", warn_merge)
        
        # Calculate demand
        detail = calculate_demand(merged, cfg, lead_time=0)
        
        # Check Dispatch_Type in Detail_Calculation
        print("\n=== Checking Dispatch_Type in Detail_Calculation ===")
        for idx, row in detail.iterrows():
            article = row['Article']
            launch_date = row.get('Launch_Date', '')
            dn_qty = row.get('Suggested_DN_Qty', 0)
            dispatch_type = row.get('Dispatch_Type', '')
            
            print(f"  {article}: Launch_Date='{launch_date}', DN_Qty={dn_qty}, Dispatch_Type='{dispatch_type}'")
            
            # Verify new SKU logic
            if (launch_date == '' or launch_date is None) and dn_qty > 0:
                if dispatch_type != "新SKU必須由Buyer首次派貨":
                    print(f"    [ERROR] {article} should show '新SKU必須由Buyer首次派貨'")
                else:
                    print(f"    [PASS] {article} correctly shows new SKU alert")
        
        # Generate summary
        summary = generate_summary(detail, cfg)
        
        # Check Enhanced_Inventory_Status and New_SKU_Alert in Summary_Report
        print("\n=== Checking Enhanced_Inventory_Status in Summary_Report ===")
        for idx, row in summary.iterrows():
            article = row['Article']
            enhanced_status = row.get('Enhanced_Inventory_Status', '')
            new_sku_alert = row.get('New_SKU_Alert', '')
            
            print(f"  {article}: Enhanced_Inventory_Status='{enhanced_status}'")
            print(f"    New_SKU_Alert='{new_sku_alert}'")
            
            # Verify if new SKU alert is correctly added to Enhanced_Inventory_Status
            if new_sku_alert:
                if new_sku_alert in enhanced_status:
                    print(f"    [PASS] New SKU alert added to Enhanced_Inventory_Status")
                else:
                    print(f"    [ERROR] New SKU alert not properly added to Enhanced_Inventory_Status")
        
        # Export result
        output_path = Path("test_new_sku_result.xlsx")
        export_to_excel(detail, summary, df_a_clean, df_b1, df_b2, output_path)
        print(f"\nResult exported to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary files
        import os
        for file in ["test_file_a.xlsx", "test_file_b.xlsx"]:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    success = test_new_sku_logic()
    if success:
        print("\n[PASS] Test completed")
    else:
        print("\n[FAIL] Test failed")