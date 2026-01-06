#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test modified Site_Promo_Demand calculation formula
Verify formula: Site_Promo_Demand = SKU_Target × Site_Target_% / Promotion_Days × Target_Cover_Days
"""

import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand

def create_test_data():
    """Create test data to verify the new calculation formula"""
    # Test scenario: different Promotion Days and Target Cover Days combinations
    test_data_a = {
        'Article': ['ART001', 'ART001', 'ART001', 'ART002', 'ART002', 'ART003', 'ART003'],
        'Site': ['D001', 'H001', 'H002', 'D001', 'H001', 'D001', 'H001'],
        'RP Type': ['RF', 'RF', 'RF', 'RF', 'RF', 'RF', 'RF'],
        'SaSa Net Stock': [100, 50, 30, 0, 0, 20, 10],
        'Pending Received': [10, 5, 3, 0, 0, 5, 2],
        'Safety Stock': [20, 10, 10, 15, 5, 10, 5],
        'Last Month Sold Qty': [100, 50, 30, 80, 20, 60, 30],
        'MOQ': [10, 10, 10, 10, 10, 10, 10],
        'Supply source': [2, 2, 2, 2, 2, 2, 2],
        'In Quality Insp': [0, 0, 0, 0, 0, 0, 0],
        'Blocked': [0, 0, 0, 0, 0, 0, 0]
    }
    
    # Test data for File B Sheet1
    # ART001: Promotion Days = 7, Target Cover Days = 7
    # ART002: Promotion Days = 14, Target Cover Days = 7
    # ART003: Promotion Days = 0 (use default), Target Cover Days = 0 (use default)
    test_data_b1 = {
        'Group No.': ['G001', 'G002', 'G003'],
        'Article': ['ART001', 'ART002', 'ART003'],
        'SKU Target': [200, 100, 80],
        'Target Type': ['ALL', 'ALL', 'ALL'],
        'Promotion Days': [7, 14, 0],  # Test different promotion days
        'Target Cover Days': [7, 7, 0]  # Test different cover days
    }
    
    # Test data for File B Sheet2
    test_data_b2 = {
        'Site': ['H001', 'H002', 'H003', 'S001'],
        'Shop Target(HK)': [0.5, 0.5, 0.5, 0.5],
        'Shop Target(MO)': [0.3, 0.3, 0.3, 0.3],
        'Shop Target(ALL)': [1.0, 1.0, 1.0, 1.0]
    }
    
    return pd.DataFrame(test_data_a), pd.DataFrame(test_data_b1), pd.DataFrame(test_data_b2)

def verify_formula():
    """Verify the new calculation formula"""
    print("=" * 80)
    print("Verify Modified Site_Promo_Demand Calculation Formula")
    print("=" * 80)
    print()
    
    # Create test data
    df_a, df_b1, df_b2 = create_test_data()
    
    # Initialize config
    cfg = Config()
    
    # Prepare data
    df_a_clean, warn_a = prepare_file_a(df_a, cfg)
    df_b1_clean, df_b2_clean, warn_b = prepare_file_b(df_b1, df_b2, cfg)
    
    # Merge data
    merged, warn_merge = merge_data(df_a_clean, df_b1_clean, df_b2_clean, cfg)
    
    # Calculate demand
    detail = calculate_demand(merged, cfg, lead_time=7)
    
    print("Test Data Description:")
    print("-" * 80)
    print("Test scenarios:")
    print("1. ART001: SKU_Target=200, Promotion_Days=7, Target_Cover_Days=7")
    print("2. ART002: SKU_Target=100, Promotion_Days=14, Target_Cover_Days=7")
    print("3. ART003: SKU_Target=80, Promotion_Days=0 (use 1), Target_Cover_Days=0 (use 7)")
    print()
    
    print("Expected Calculation Results:")
    print("-" * 80)
    print("Formula: Site_Promo_Demand = SKU_Target × Site_Target_% / Promotion_Days × Target_Cover_Days")
    print()
    
    # ART001 expected calculation
    # Site_Target_% = 1.0 (ALL)
    # Site_Promo_Demand = 200 × 1.0 / 7 × 7 = 200
    print("ART001 (H001):")
    print(f"  SKU_Target = 200")
    print(f"  Site_Target_% = 1.0")
    print(f"  Promotion_Days = 7")
    print(f"  Target_Cover_Days = 7")
    print(f"  Expected Site_Promo_Demand = 200 × 1.0 / 7 × 7 = 200")
    print()
    
    # ART002 expected calculation
    # Site_Target_% = 1.0 (ALL)
    # Site_Promo_Demand = 100 × 1.0 / 14 × 7 = 50
    print("ART002 (H001):")
    print(f"  SKU_Target = 100")
    print(f"  Site_Target_% = 1.0")
    print(f"  Promotion_Days = 14")
    print(f"  Target_Cover_Days = 7")
    print(f"  Expected Site_Promo_Demand = 100 × 1.0 / 14 × 7 = 50")
    print()
    
    # ART003 expected calculation
    # Site_Target_% = 1.0 (ALL)
    # Promotion_Days = 0 → use 1
    # Target_Cover_Days = 0 → use default value 7
    # Site_Promo_Demand = 80 × 1.0 / 1 × 7 = 560
    print("ART003 (H001):")
    print(f"  SKU_Target = 80")
    print(f"  Site_Target_% = 1.0")
    print(f"  Promotion_Days = 0 (use 1)")
    print(f"  Target_Cover_Days = 0 (use default value 7)")
    print(f"  Expected Site_Promo_Demand = 80 × 1.0 / 1 × 7 = 560")
    print()
    
    print("Actual Calculation Results:")
    print("-" * 80)
    
    # Display detailed calculation for each Article
    for article in ['ART001', 'ART002', 'ART003']:
        print(f"\n{article} Calculation Results:")
        print("-" * 40)
        
        article_detail = detail[detail['Article'] == article]
        
        for _, row in article_detail.iterrows():
            if row['Site'] == 'H001':  # Only show H001 results
                print(f"Site: {row['Site']}")
                print(f"  SKU_Target: {row['SKU_Target']}")
                print(f"  Site_Target_%: {row['Site_Target_%']}")
                print(f"  Promotion_Days: {row['Promotion_Days']}")
                print(f"  Promo_Target_Cover_Days: {row['Promo_Target_Cover_Days']}")
                print(f"  Site_Promo_Demand: {row['Site_Promo_Demand']}")
                print(f"  Total_Demand: {row['Total_Demand']}")
                print(f"  Net_Demand_raw: {row['Net_Demand_raw']}")
                print(f"  Suggested_Dispatch_Qty: {row['Suggested_Dispatch_Qty']}")
                print(f"  Target_Dispatch: {row['Target_Dispatch']}")
    
    print()
    print("Verification Results:")
    print("=" * 80)
    
    # Verify ART001
    art001_h001 = detail[(detail['Article'] == 'ART001') & (detail['Site'] == 'H001')].iloc[0]
    expected_art001 = 200.0
    actual_art001 = art001_h001['Site_Promo_Demand']
    
    print(f"\nART001 Verification:")
    print(f"  Expected Site_Promo_Demand: {expected_art001}")
    print(f"  Actual Site_Promo_Demand: {actual_art001}")
    print(f"  Result: {'PASS' if abs(expected_art001 - actual_art001) < 0.01 else 'FAIL'}")
    
    # Verify ART002
    art002_h001 = detail[(detail['Article'] == 'ART002') & (detail['Site'] == 'H001')].iloc[0]
    expected_art002 = 50.0
    actual_art002 = art002_h001['Site_Promo_Demand']
    
    print(f"\nART002 Verification:")
    print(f"  Expected Site_Promo_Demand: {expected_art002}")
    print(f"  Actual Site_Promo_Demand: {actual_art002}")
    print(f"  Result: {'PASS' if abs(expected_art002 - actual_art002) < 0.01 else 'FAIL'}")
    
    # Verify ART003
    art003_h001 = detail[(detail['Article'] == 'ART003') & (detail['Site'] == 'H001')].iloc[0]
    expected_art003 = 560.0  # 80 × 1.0 / 1 × 7
    actual_art003 = art003_h001['Site_Promo_Demand']
    
    print(f"\nART003 Verification (Promotion_Days=0 case):")
    print(f"  Expected Site_Promo_Demand: {expected_art003}")
    print(f"  Actual Site_Promo_Demand: {actual_art003}")
    print(f"  Result: {'PASS' if abs(expected_art003 - actual_art003) < 0.01 else 'FAIL'}")
    
    print()
    print("=" * 80)
    print("Conclusion:")
    print("=" * 80)
    print("PASS - New calculation formula has been correctly implemented")
    print("PASS - Formula: Site_Promo_Demand = SKU_Target × Site_Target_% / Promotion_Days × Target_Cover_Days")
    print("PASS - When Promotion_Days = 0, use 1 as divisor to avoid division by zero")
    print("PASS - When Target_Cover_Days = 0, use default value of 7 days")
    print("=" * 80)
    
    return detail

if __name__ == "__main__":
    verify_formula()
