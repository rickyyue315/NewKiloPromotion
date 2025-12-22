import pandas as pd
from promo_calculator import (
    Config, 
    prepare_file_a, 
    prepare_file_b, 
    merge_data, 
    calculate_demand, 
    generate_summary
)

def create_comprehensive_test_data():
    """Create comprehensive test data with multiple scenarios"""
    # File A test data - include multiple scenarios
    test_data_a = {
        "Article": ["TEST001", "TEST002", "TEST003"],
        "Site": ["HA01", "D001", "HB01"],
        "RP Type": ["RF", "RF", "RF"],
        "SaSa Net Stock": [10, 50, 20],  # D001 has 50, others have 10 and 20
        "Pending Received": [5, 10, 5],
        "Safety Stock": [20, 30, 15],
        "Last Month Sold Qty": [30, 25, 20],
        "MOQ": [6, 6, 6],
        "Supply source": [2, 2, 2],
        "Launch Date": ["2023-01-01", "2023-02-01", "2023-03-01"]
    }
    
    # File B Sheet1 test data - create different demand levels
    test_data_b1 = {
        "Group No.": ["G001", "G001", "G001"],
        "Article": ["TEST001", "TEST002", "TEST003"],
        "SKU Target": [100, 150, 80],
        "Target Type": ["ALL", "HK", "ALL"],
        "Promotion Days": [7, 5, 3],
        "Target Cover Days": [7, 0, 5]
    }
    
    # File B Sheet2 test data
    test_data_b2 = {
        "Site": ["HA01", "D001", "HB01"],
        "Shop Target(HK)": [0.3, 0.2, 0.4],
        "Shop Target(MO)": [0.4, 0.3, 0.3],
        "Shop Target(ALL)": [0.5, 0.4, 0.5]
    }
    
    return test_data_a, test_data_b1, test_data_b2

def test_comprehensive_scenarios():
    """Test multiple scenarios for D001 stock shortage"""
    print("=== Comprehensive D001 Stock Shortage Test ===")
    
    # Create test data
    test_data_a, test_data_b1, test_data_b2 = create_comprehensive_test_data()
    
    # Convert to DataFrame
    df_a_raw = pd.DataFrame(test_data_a)
    df_b1_raw = pd.DataFrame(test_data_b1)
    df_b2_raw = pd.DataFrame(test_data_b2)
    
    # Set configuration
    config = Config()
    
    # Prepare data
    df_a_clean, warn_a = prepare_file_a(df_a_raw, config)
    df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, config)
    
    # Merge data
    merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, config)
    
    # Calculate demand
    detail = calculate_demand(merged, config, lead_time=0)
    
    # Generate summary
    summary = generate_summary(detail, config)
    
    # Display summary results
    print("Summary Report Results:")
    summary_cols = [
        "Article",
        "D001_SaSa_Net_Stock",
        "Total_Suggested_DN_Qty",
        "Total_Target_Dispatch",
        "D001_Stock_Shortage_Alert"
    ]
    summary_display = summary[summary_cols]
    for _, row in summary_display.iterrows():
        print(f"Article: {row['Article']}")
        print(f"  D001_Stock: {row['D001_SaSa_Net_Stock']}")
        print(f"  Total_Suggested_DN_Qty: {row['Total_Suggested_DN_Qty']}")
        print(f"  Total_Target_Dispatch: {row['Total_Target_Dispatch']}")
        print(f"  D001_Stock_Shortage_Alert: {row['D001_Stock_Shortage_Alert']}")
        print()
    
    # Verify D001 shortage logic for each article
    print("=== Verification Results ===")
    all_correct = True
    
    for _, row in summary.iterrows():
        article = row["Article"]
        d001_stock = row["D001_SaSa_Net_Stock"]
        total_suggested_dn_qty = row["Total_Suggested_DN_Qty"]
        total_target_dispatch = row["Total_Target_Dispatch"]
        shortage_alert = row["D001_Stock_Shortage_Alert"]
        enhanced_status = row["Enhanced_Inventory_Status"]
        
        # Check if shortage alert is correct
        expected_shortage = ""
        if d001_stock < total_suggested_dn_qty or d001_stock < total_target_dispatch:
            expected_shortage = "D001 not enough for RP team to add dispatch"
        
        print(f"Article: {article}")
        print(f"  D001_Stock: {d001_stock}")
        print(f"  Total_Suggested_DN_Qty: {total_suggested_dn_qty}")
        print(f"  Total_Target_Dispatch: {total_target_dispatch}")
        print(f"  Expected Shortage Alert: {expected_shortage}")
        print(f"  Actual Shortage Alert: {shortage_alert}")
        
        # Check if alert is correctly included in enhanced status
        if expected_shortage:
            if expected_shortage in enhanced_status:
                print("  Status: CORRECT - Shortage alert properly included in enhanced status")
            else:
                print("  Status: INCORRECT - Shortage alert missing from enhanced status")
                all_correct = False
        else:
            if not shortage_alert and expected_shortage not in enhanced_status:
                print("  Status: CORRECT - No shortage alert when not needed")
            else:
                print("  Status: INCORRECT - Unexpected shortage alert")
                all_correct = False
        print()
    
    # Overall result
    print("\n=== OVERALL TEST RESULT ===")
    if all_correct:
        print("ALL TESTS PASSED! D001 stock shortage logic is working correctly across all scenarios.")
    else:
        print("SOME TESTS FAILED! Please check the implementation.")
    
    return detail, summary

if __name__ == "__main__":
    test_comprehensive_scenarios()