import pandas as pd
from pathlib import Path
from promo_calculator import (
    Config, 
    prepare_file_a, 
    prepare_file_b, 
    merge_data, 
    calculate_demand, 
    generate_summary,
    export_to_excel
)

def create_test_data_with_d001_shortage():
    """Create test data that will trigger D001 stock shortage"""
    # File A test data - include D001 with low stock
    test_data_a = {
        "Article": ["TEST001", "TEST001", "TEST002", "TEST002", "TEST003"],
        "Site": ["HA01", "D001", "HA01", "HB87", "HC01"],
        "RP Type": ["RF", "RF", "ND", "RF", "RF"],
        "SaSa Net Stock": [10, 30, 15, 5, 12],  # D001 has 30, others have various amounts
        "Pending Received": [5, 10, 2, 3, 6],
        "Safety Stock": [20, 30, 25, 18, 22],
        "Last Month Sold Qty": [30, 25, 35, 28, 32],
        "MOQ": [6, 6, 8, 6, 10],
        "Supply source": [2, 2, 1, 2, 4],
        "Launch Date": ["2023-01-01", "", "2023-02-01", "2023-03-01", ""]
    }
    
    # File B Sheet1 test data - create high demand
    test_data_b1 = {
        "Group No.": ["G001", "G001", "G002"],
        "Article": ["TEST001", "TEST002", "TEST003"],
        "SKU Target": [100, 150, 80],
        "Target Type": ["ALL", "HK", "MO"],
        "Promotion Days": [7, 5, 10],
        "Target Cover Days": [7, 0, 5]
    }
    
    # File B Sheet2 test data
    test_data_b2 = {
        "Site": ["HA01", "HB87", "HC01", "D001"],
        "Shop Target(HK)": [0.3, 0.2, 0.25, 0],
        "Shop Target(MO)": [0.4, 0.3, 0.35, 0],
        "Shop Target(ALL)": [0.5, 0.4, 0.45, 0]
    }
    
    return test_data_a, test_data_b1, test_data_b2

def test_d001_stock_shortage_logic():
    """Test D001 stock shortage alert logic"""
    print("=== Test D001 Stock Shortage Alert Logic ===")
    
    # Create test data
    test_data_a, test_data_b1, test_data_b2 = create_test_data_with_d001_shortage()
    
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
    
    # Display summary results with focus on D001 shortage
    print("Summary Report Results (Focus on D001 Stock Shortage):")
    summary_cols = [
        "Article", 
        "D001_SaSa_Net_Stock", 
        "Total_Suggested_DN_Qty", 
        "Total_Target_Dispatch",
        "Enhanced_Inventory_Status",
        "D001_Stock_Shortage_Alert"
    ]
    summary_display = summary[summary_cols]
    for _, row in summary_display.iterrows():
        print(f"Article: {row['Article']}")
        print(f"  D001_SaSa_Net_Stock: {row['D001_SaSa_Net_Stock']}")
        print(f"  Total_Suggested_DN_Qty: {row['Total_Suggested_DN_Qty']}")
        print(f"  Total_Target_Dispatch: {row['Total_Target_Dispatch']}")
        print(f"  Enhanced_Inventory_Status: {row['Enhanced_Inventory_Status']}")
        print(f"  D001_Stock_Shortage_Alert: {row['D001_Stock_Shortage_Alert']}")
        print()
    
    # Verify D001 shortage logic
    print("=== Verify D001 Stock Shortage Calculation ===")
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
        print(f"  D001_SaSa_Net_Stock: {d001_stock}")
        print(f"  Total_Suggested_DN_Qty: {total_suggested_dn_qty}")
        print(f"  Total_Target_Dispatch: {total_target_dispatch}")
        print(f"  Expected Shortage Alert: '{expected_shortage}'")
        print(f"  Actual Shortage Alert: '{shortage_alert}'")
        print(f"  Enhanced Status: '{enhanced_status}'")
        
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
    
    # Test export function
    print("=== Test Export Function ===")
    output_path = Path("test_d001_shortage_result.xlsx")
    try:
        export_to_excel(detail, summary, df_a_clean, df_b1, df_b2, output_path)
        print(f"Successfully exported to: {output_path}")
        print("Please check the following worksheets in the Excel file:")
        print("  - Summary_Report: should contain D001_Stock_Shortage_Alert column")
    except Exception as e:
        print(f"Export failed: {e}")
        all_correct = False
    
    # Overall result
    print("\n=== OVERALL TEST RESULT ===")
    if all_correct:
        print("ALL TESTS PASSED! D001 stock shortage logic is working correctly.")
    else:
        print("SOME TESTS FAILED! Please check the implementation.")
    
    return detail, summary

if __name__ == "__main__":
    test_d001_stock_shortage_logic()