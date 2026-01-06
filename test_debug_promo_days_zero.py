#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to investigate Promotion_Days = 0 issue
"""

import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def create_test_data():
    """Create simple test data for debugging"""
    test_data_a = {
        'Article': ['ART003'],
        'Site': ['H001'],
        'RP Type': ['RF'],
        'SaSa Net Stock': [10],
        'Pending Received': [2],
        'Safety Stock': [5],
        'Last Month Sold Qty': [30],
        'MOQ': [10],
        'Supply source': [2],
        'In Quality Insp': [0],
        'Blocked': [0]
    }
    
    test_data_b1 = {
        'Group No.': ['G003'],
        'Article': ['ART003'],
        'SKU Target': [80],
        'Target Type': ['ALL'],
        'Promotion Days': [0],  # Test Promotion_Days = 0
        'Target Cover Days': [0]  # Test Target_Cover_Days = 0
    }
    
    test_data_b2 = {
        'Site': ['H001'],
        'Shop Target(HK)': [0.5],
        'Shop Target(MO)': [0.3],
        'Shop Target(ALL)': [1.0]
    }
    
    return pd.DataFrame(test_data_a), pd.DataFrame(test_data_b1), pd.DataFrame(test_data_b2)

def debug_promo_days_zero():
    """Debug Promotion_Days = 0 issue"""
    print("=" * 80)
    print("Debug Promotion_Days = 0 Issue")
    print("=" * 80)
    print()
    
    # Create test data
    df_a, df_b1, df_b2 = create_test_data()
    
    # Initialize config
    cfg = Config()
    
    # Prepare data
    print("Step 1: Prepare File A")
    print("-" * 80)
    df_a_clean, warn_a = prepare_file_a(df_a, cfg)
    print(f"File A columns: {df_a_clean.columns.tolist()}")
    print(f"File A data:\n{df_a_clean}")
    print()
    
    print("Step 2: Prepare File B")
    print("-" * 80)
    df_b1_clean, df_b2_clean, warn_b = prepare_file_b(df_b1, df_b2, cfg)
    print(f"File B1 columns: {df_b1_clean.columns.tolist()}")
    print(f"File B1 data:\n{df_b1_clean}")
    print(f"File B2 columns: {df_b2_clean.columns.tolist()}")
    print(f"File B2 data:\n{df_b2_clean}")
    print()
    
    print("Step 3: Merge Data")
    print("-" * 80)
    merged, warn_merge = merge_data(df_a_clean, df_b1_clean, df_b2_clean, cfg)
    print(f"Merged columns: {merged.columns.tolist()}")
    print(f"Merged data:\n{merged}")
    print()
    
    print("Step 4: Check Is_Promo_SKU flag")
    print("-" * 80)
    print(f"Is_Promo_SKU: {merged['Is_Promo_SKU'].values}")
    print(f"SKU_Target: {merged['SKU_Target'].values}")
    print(f"Site_Target_%: {merged['Site_Target_%'].values}")
    print(f"Promotion_Days: {merged['Promotion_Days'].values}")
    print(f"Promo_Target_Cover_Days: {merged['Promo_Target_Cover_Days'].values}")
    print()
    
    print("Step 5: Calculate Demand")
    print("-" * 80)
    detail = calculate_demand(merged, cfg, lead_time=7)
    print(f"Detail data:\n{detail}")
    print()
    
    print("Step 6: Check Site_Promo_Demand calculation")
    print("-" * 80)
    print(f"Site_Promo_Demand: {detail['Site_Promo_Demand'].values}")
    print(f"Total_Demand: {detail['Total_Demand'].values}")
    print()
    
    print("Step 7: Manual calculation verification")
    print("-" * 80)
    sku_target = 80
    site_target_pct = 1.0
    promotion_days = 0
    target_cover_days = 0
    
    # Apply same logic as in calculate_demand
    promo_days_safe = promotion_days if promotion_days > 0 else 1
    effective_target_cover_days = target_cover_days if target_cover_days > 0 else 7
    
    manual_result = sku_target * site_target_pct / promo_days_safe * effective_target_cover_days
    print(f"Manual calculation:")
    print(f"  SKU_Target = {sku_target}")
    print(f"  Site_Target_% = {site_target_pct}")
    print(f"  Promotion_Days = {promotion_days} → promo_days_safe = {promo_days_safe}")
    print(f"  Target_Cover_Days = {target_cover_days} → effective_target_cover_days = {effective_target_cover_days}")
    print(f"  Manual Site_Promo_Demand = {sku_target} × {site_target_pct} / {promo_days_safe} × {effective_target_cover_days} = {manual_result}")
    print()
    
    print("Step 8: Check Effective_Target_Cover_Days in detail")
    print("-" * 80)
    print(f"Effective_Target_Cover_Days: {detail['Effective_Target_Cover_Days'].values}")
    print()
    
    print("=" * 80)
    print("Conclusion:")
    print("=" * 80)
    print(f"Expected Site_Promo_Demand: {manual_result}")
    print(f"Actual Site_Promo_Demand: {detail['Site_Promo_Demand'].values[0]}")
    print(f"Match: {abs(manual_result - detail['Site_Promo_Demand'].values[0]) < 0.01}")
    print("=" * 80)
    
    return detail

if __name__ == "__main__":
    debug_promo_days_zero()
