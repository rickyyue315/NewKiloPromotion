import pandas as pd
from promo_calculator import Config, prepare_file_a, prepare_file_b, merge_data, calculate_demand, generate_summary

def test_new_sku_logic():
    """Test new SKU logic: Launch Date is blank and Suggested_DN_Qty > 0 should show '新SKU必須由Buyer首次派貨'"""
    
    config = Config()
    
    # Create mock File A data - including new SKUs and normal SKUs
    file_a_data = {
        'Article': ['NEW001', 'NEW002', 'NORMAL001', 'NORMAL002'],
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'RP Type': ['ND', 'ND', 'ND', 'ND'],
        'Supply source': [2, 1, 2, 4],
        'SaSa Net Stock': [10, 20, 30, 40],
        'Pending Received': [0, 0, 0, 0],
        'Safety Stock': [5, 5, 5, 5],
        'Last Month Sold Qty': [0, 0, 50, 100],
        'MOQ': [10, 10, 10, 10],
        'Launch Date': ['', ' ', '2023-01-01', '2023-02-01'],  # New SKUs: blank and space, Normal SKUs: have dates
    }
    
    # Create mock File B Sheet1 data
    file_b1_data = {
        'Group No.': ['G001', 'G002', 'G003', 'G004'],
        'Article': ['NEW001', 'NEW002', 'NORMAL001', 'NORMAL002'],
        'SKU Target': [100, 80, 60, 40],
        'Target Type': ['ALL', 'ALL', 'ALL', 'ALL'],
        'Promotion Days': [5, 5, 5, 5],
    }
    
    # Create mock File B Sheet2 data
    file_b2_data = {
        'Site': ['ND001', 'ND002', 'ND003', 'ND004'],
        'Shop Target(HK)': [0.5, 0.5, 0.5, 0.5],
        'Shop Target(MO)': [0.3, 0.3, 0.3, 0.3],
        'Shop Target(ALL)': [0.2, 0.2, 0.2, 0.2],
    }
    
    # Convert to DataFrame
    df_a_raw = pd.DataFrame(file_a_data)
    df_b1_raw = pd.DataFrame(file_b1_data)
    df_b2_raw = pd.DataFrame(file_b2_data)
    
    # Process data
    df_a_clean, warn_a = prepare_file_a(df_a_raw, config)
    df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, config)
    merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, config)
    detail = calculate_demand(merged, config, lead_time=7)
    summary = generate_summary(detail, config)
    
    print("=== Test New SKU Logic ===")
    print()
    
    # Check Dispatch_Type in Detail_Calculation
    print("Detail_Calculation Results:")
    print("Article\tSite\tLaunch_Date\tSuggested_DN_Qty\tDispatch_Type")
    print("-" * 80)
    
    new_sku_count = 0
    for _, row in detail.iterrows():
        article = row['Article']
        site = row['Site']
        launch_date = row['Launch_Date']
        dn_qty = row['Suggested_DN_Qty']
        dispatch_type = row['Dispatch_Type']
        
        print(f"{article}\t{site}\t'{launch_date}'\t\t{dn_qty}\t\t{dispatch_type}")
        
        # Check new SKU logic
        is_launch_blank = (launch_date == "" or launch_date == " ")
        if is_launch_blank and dn_qty > 0:
            expected_type = "新SKU必須由Buyer首次派貨"
            if dispatch_type == expected_type:
                print(f"  CORRECT: New SKU {article} shows '{dispatch_type}'")
                new_sku_count += 1
            else:
                print(f"  ERROR: New SKU {article} should show '{expected_type}', but shows '{dispatch_type}'")
        print()
    
    # Check New_SKU_Alert in Summary_Report
    print("Summary_Report Results:")
    print("Article\tTotal_Suggested_DN_Qty\tNew_SKU_Alert")
    print("-" * 60)
    
    summary_new_sku_count = 0
    for _, row in summary.iterrows():
        article = row['Article']
        total_dn_qty = row['Total_Suggested_DN_Qty']
        new_sku_alert = row['New_SKU_Alert']
        
        print(f"{article}\t{total_dn_qty}\t\t\t{new_sku_alert}")
        
        if new_sku_alert == "新SKU必須由Buyer首次派貨":
            print(f"  CORRECT: Summary_Report shows new SKU alert for {article}")
            summary_new_sku_count += 1
        print()
    
    # Summarize test results
    print("=== Test Results Summary ===")
    print(f"New SKUs detected in Detail: {new_sku_count}")
    print(f"New SKUs detected in Summary: {summary_new_sku_count}")
    
    expected_new_skus = 2  # NEW001 and NEW002
    if new_sku_count == expected_new_skus and summary_new_sku_count == expected_new_skus:
        print("TEST PASSED: New SKU logic works correctly")
        return True
    else:
        print(f"TEST FAILED: Expected {expected_new_skus} new SKUs, but detected {new_sku_count} in Detail and {summary_new_sku_count} in Summary")
        return False

if __name__ == "__main__":
    test_new_sku_logic()