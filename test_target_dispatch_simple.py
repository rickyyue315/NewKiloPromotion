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

def create_test_data():
    """Create test data"""
    # File A test data
    test_data_a = {
        "Article": ["TEST001", "TEST001", "TEST002", "TEST002", "TEST003"],
        "Site": ["HA01", "HB87", "HA01", "HB87", "HC01"],
        "RP Type": ["RF", "RF", "ND", "RF", "RF"],
        "SaSa Net Stock": [10, 5, 15, 8, 12],
        "Pending Received": [5, 3, 2, 4, 6],
        "Safety Stock": [20, 15, 25, 18, 22],
        "Last Month Sold Qty": [30, 25, 35, 28, 32],
        "MOQ": [6, 6, 8, 6, 10],
        "Supply source": [2, 2, 1, 2, 4],
        "Launch Date": ["2023-01-01", "", "2023-02-01", "2023-03-01", ""]
    }
    
    # File B Sheet1 test data
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

def test_target_dispatch_logic():
    """Test Target Dispatch logic"""
    print("=== Test Target Dispatch Logic ===\n")
    
    # Create test data
    test_data_a, test_data_b1, test_data_b2 = create_test_data()
    
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
    
    # Display detail results
    print("Detail Calculation Results:")
    detail_cols = [
        "Article", "Site", "RP_Type", "Site_Promo_Demand", 
        "SaSa_Net_Stock", "Pending_Received", "MOQ", 
        "Target_Dispatch", "Suggested_Dispatch_Qty"
    ]
    detail_display = detail[detail_cols]
    for _, row in detail_display.iterrows():
        print(f"Article: {row['Article']}, Site: {row['Site']}, RP_Type: {row['RP_Type']}")
        print(f"  Site_Promo_Demand: {row['Site_Promo_Demand']}, SaSa_Net_Stock: {row['SaSa_Net_Stock']}, Pending_Received: {row['Pending_Received']}")
        print(f"  MOQ: {row['MOQ']}, Target_Dispatch: {row['Target_Dispatch']}, Suggested_Dispatch_Qty: {row['Suggested_Dispatch_Qty']}")
        print()
    
    # Display summary results
    print("Summary Report Results:")
    summary_cols = [
        "Article", "Total_Demand", "Total_Target_Dispatch", 
        "Total_Dispatch"
    ]
    summary_display = summary[summary_cols]
    for _, row in summary_display.iterrows():
        print(f"Article: {row['Article']}")
        print(f"  Total_Demand: {row['Total_Demand']}, Total_Target_Dispatch: {row['Total_Target_Dispatch']}")
        print(f"  Total_Dispatch: {row['Total_Dispatch']}")
        print()
    
    # Verify Target Dispatch calculation
    print("=== Verify Target Dispatch Calculation ===")
    all_correct = True
    for _, row in detail.iterrows():
        article = row["Article"]
        site = row["Site"]
        site_promo_demand = row["Site_Promo_Demand"]
        sasa_net_stock = row["SaSa_Net_Stock"]
        pending_received = row["Pending_Received"]
        moq = row["MOQ"]
        target_dispatch = row["Target_Dispatch"]
        
        # Manual calculation of Target Dispatch
        raw_value = site_promo_demand - sasa_net_stock - pending_received
        if raw_value > 0 and moq > 0:
            expected_target_dispatch = round(raw_value / moq) * moq
            expected_target_dispatch = max(expected_target_dispatch, moq)
        else:
            expected_target_dispatch = 0
        
        print(f"Article: {article}, Site: {site}")
        print(f"  Calculation: {site_promo_demand} - {sasa_net_stock} - {pending_received} = {raw_value}")
        print(f"  Expected Target Dispatch: {expected_target_dispatch}")
        print(f"  Actual Target Dispatch: {target_dispatch}")
        
        if target_dispatch == expected_target_dispatch:
            print("  Status: CORRECT")
        else:
            print("  Status: INCORRECT")
            all_correct = False
        print()
    
    # Verify Total_Target_Dispatch in Summary
    print("=== Verify Total_Target_Dispatch in Summary ===")
    for _, row in summary.iterrows():
        article = row["Article"]
        total_target_dispatch = row["Total_Target_Dispatch"]
        
        # Calculate the sum of Target Dispatch for this Article in Detail
        detail_rows = detail[detail["Article"] == article]
        expected_total = detail_rows["Target_Dispatch"].sum()
        
        print(f"Article: {article}")
        print(f"  Expected Total_Target_Dispatch: {expected_total}")
        print(f"  Actual Total_Target_Dispatch: {total_target_dispatch}")
        
        if total_target_dispatch == expected_total:
            print("  Status: CORRECT")
        else:
            print("  Status: INCORRECT")
            all_correct = False
        print()
    
    # Test export function
    print("=== Test Export Function ===")
    output_path = Path("test_target_dispatch_result.xlsx")
    try:
        export_to_excel(detail, summary, df_a_clean, df_b1, df_b2, output_path)
        print(f"Successfully exported to: {output_path}")
        print("Please check the following worksheets in the Excel file:")
        print("  - Detail_Calculation: should contain Target_Dispatch column")
        print("  - Summary_Report: should contain Total_Target_Dispatch column")
    except Exception as e:
        print(f"Export failed: {e}")
        all_correct = False
    
    # Overall result
    print("\n=== OVERALL TEST RESULT ===")
    if all_correct:
        print("ALL TESTS PASSED! Target Dispatch logic is working correctly.")
    else:
        print("SOME TESTS FAILED! Please check the implementation.")
    
    return detail, summary

if __name__ == "__main__":
    test_target_dispatch_logic()