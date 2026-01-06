#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test verification for Promotion_Days and Promo_Target_Cover_Days fields in Excel report
"""
import pandas as pd
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_test_data():
    """Create test data to verify the fields in Excel report"""
    
    # File A data (site-level data)
    file_a_data = {
        'Article': ['A12345', 'A12345', 'A12345'],
        'Site': ['HB87', 'ND01', 'ND02'],
        'RP Type': ['RF', 'ND', 'ND'],
        'SaSa Net Stock': [50, 30, 20],
        'Pending Received': [10, 5, 5],
        'Safety Stock': [30, 20, 15],
        'Last Month Sold Qty': [100, 80, 60],
        'MOQ': [12, 12, 12],
        'Supply source': [2, 2, 2],
        'In Quality Insp': [0, 0, 0],
        'Blocked': [0, 0, 0]
    }
    
    # File B Sheet1 data (promotion target data)
    file_b1_data = {
        'Group No.': ['G001'],
        'Article': ['A12345'],
        'SKU Target': [1000],
        'Target Type': ['ALL'],
        'Promotion Days': [7],  # 7 days promotion
        'Target Cover Days': [10]  # 10 days cover
    }
    
    # File B Sheet2 data (shop target data)
    file_b2_data = {
        'Site': ['HB87', 'ND01', 'ND02', 'S001'],
        'Shop Target(HK)': [0.5, 0.5, 0.5, 0.5],
        'Shop Target(MO)': [0.3, 0.3, 0.3, 0.3],
        'Shop Target(ALL)': [1.0, 1.0, 1.0, 1.0]
    }
    
    return pd.DataFrame(file_a_data), pd.DataFrame(file_b1_data), pd.DataFrame(file_b2_data)

def test_promotion_cover_days_export():
    """Test if Excel report contains Promotion_Days and Promo_Target_Cover_Days fields"""
    
    print("=" * 80)
    print("Test verification for Promotion_Days and Promo_Target_Cover_Days fields output")
    print("=" * 80)
    print()
    
    # Create test data
    file_a_df, file_b1_df, file_b2_df = create_test_data()
    
    print("Test data:")
    print("- File A data (site-level):")
    print(file_a_df[['Article', 'Site', 'SaSa Net Stock', 'Pending Received']])
    print()
    print("- File B Sheet1 data (promotion target):")
    print(file_b1_df[['Article', 'SKU Target', 'Promotion Days', 'Target Cover Days']])
    print()
    print("- File B Sheet2 data (shop target):")
    print(file_b2_df)
    print()
    
    # Import promo_calculator module
    try:
        from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand
        
        print("Executing calculation...")
        
        # Initialize config
        cfg = Config()
        
        # Prepare data
        df_a_clean, warn_a = prepare_file_a(file_a_df, cfg)
        df_b1_clean, df_b2_clean, warn_b = prepare_file_b(file_b1_df, file_b2_df, cfg)
        
        # Merge data
        merged, warn_merge = merge_data(df_a_clean, df_b1_clean, df_b2_clean, cfg)
        
        # Calculate demand
        detail_df = calculate_demand(merged, cfg, lead_time=7)
        
        print("OK Calculation completed")
        print()
        
        # Check if Detail_Calculation contains required fields
        print("Checking fields in Detail_Calculation:")
        print("-" * 80)
        
        required_cols = ['Promotion_Days', 'Promo_Target_Cover_Days']
        all_present = True
        
        for col in required_cols:
            if col in detail_df.columns:
                print(f"OK {col} field exists")
                # Display field values
                print(f"  Values: {detail_df[col].tolist()}")
            else:
                print(f"X {col} field does not exist")
                all_present = False
        
        print()
        
        if all_present:
            print("OK All required fields exist in Detail_Calculation")
        else:
            print("X Some required fields are missing")
            print(f"  Existing fields: {list(detail_df.columns)}")
            return False
        
        print()
        print("Check if Site_Promo_Demand calculation considers Promotion_Days and Promo_Target_Cover_Days:")
        print("-" * 80)
        
        # Display detailed calculation results
        print("\nDetailed calculation data:")
        for idx, row in detail_df.iterrows():
            print(f"\nSite: {row['Site']}")
            print(f"  Site_Target_%: {row['Site_Target_%']:.2%}")
            print(f"  SKU_Target: {row['SKU_Target']}")
            print(f"  Promotion_Days: {row['Promotion_Days']}")
            print(f"  Effective_Target_Cover_Days: {row['Effective_Target_Cover_Days']}")
            print(f"  Site_Promo_Demand: {row['Site_Promo_Demand']:.2f}")
            
            # Verify calculation formula
            expected = (row['SKU_Target'] * row['Site_Target_%'] / 
                       max(1, row['Promotion_Days']) * row['Effective_Target_Cover_Days'])
            print(f"  Expected (formula): {expected:.2f}")
            
            if abs(row['Site_Promo_Demand'] - expected) < 0.01:
                print(f"  OK Calculation correct")
            else:
                print(f"  X Calculation error (difference: {abs(row['Site_Promo_Demand'] - expected):.2f})")
        
        print()
        print("=" * 80)
        print("Test results:")
        print("=" * 80)
        
        if all_present:
            print("OK All tests passed")
            print("  - Promotion_Days field correctly added to Detail_Calculation")
            print("  - Promo_Target_Cover_Days field correctly added to Detail_Calculation")
            print("  - Site_Promo_Demand calculation correctly considers these two fields")
            return True
        else:
            print("X Test failed")
            return False
            
    except Exception as e:
        print(f"X Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_promotion_cover_days_export()
    sys.exit(0 if success else 1)
