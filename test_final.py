import pandas as pd
from promo_calculator import generate_summary, Config

def test_final():
    """Test final implementation"""
    
    # Test case 1: Positive inventory difference
    test_data_1 = pd.DataFrame({
        'Group_No': ['G001', 'G001'],
        'Article': ['TEST001', 'TEST001'],
        'Site': ['D001', 'HA1'],
        'RP_Type': ['RF', 'RF'],
        'Supply_source': [2, 2],
        'SaSa_Net_Stock': [150, 50],
        'Pending_Received': [10, 5],
        'Total_Demand': [80, 80],
        'Suggested_Dispatch_Qty': [0, 0],
        'In_Quality_Insp': [0, 0],
        'Blocked': [0, 0]
    })
    
    # Test case 2: Negative inventory difference
    test_data_2 = pd.DataFrame({
        'Group_No': ['G002', 'G002'],
        'Article': ['TEST002', 'TEST002'],
        'Site': ['D001', 'HA1'],
        'RP_Type': ['RF', 'RF'],
        'Supply_source': [2, 2],
        'SaSa_Net_Stock': [30, 10],
        'Pending_Received': [5, 2],
        'Total_Demand': [100, 100],
        'Suggested_Dispatch_Qty': [0, 0],
        'In_Quality_Insp': [0, 0],
        'Blocked': [0, 0]
    })
    
    cfg = Config()
    
    print("=== Test Final Implementation ===")
    
    # Test case 1
    summary_1 = generate_summary(test_data_1, cfg)
    effective_inv_1 = summary_1["Effective_Inventory"].iloc[0]
    total_demand_1 = summary_1["Total_Demand"].iloc[0]
    inv_diff_1 = summary_1["Inventory_Difference"].iloc[0]
    status_1 = summary_1["Enhanced_Inventory_Status"].iloc[0]
    
    print(f"\nTest Case 1 (Positive Difference):")
    print(f"Effective_Inventory: {effective_inv_1}")
    print(f"Total_Demand: {total_demand_1}")
    print(f"Inventory_Difference: {inv_diff_1}")
    print(f"Expected Difference: {effective_inv_1 - total_demand_1}")
    print(f"Status: {status_1}")
    
    # Test case 2
    summary_2 = generate_summary(test_data_2, cfg)
    effective_inv_2 = summary_2["Effective_Inventory"].iloc[0]
    total_demand_2 = summary_2["Total_Demand"].iloc[0]
    inv_diff_2 = summary_2["Inventory_Difference"].iloc[0]
    status_2 = summary_2["Enhanced_Inventory_Status"].iloc[0]
    
    print(f"\nTest Case 2 (Negative Difference):")
    print(f"Effective_Inventory: {effective_inv_2}")
    print(f"Total_Demand: {total_demand_2}")
    print(f"Inventory_Difference: {inv_diff_2}")
    print(f"Expected Difference: {effective_inv_2 - total_demand_2}")
    print(f"Status: {status_2}")
    
    print(f"\n=== Feature Verification ===")
    feature_1_ok = (inv_diff_1 == effective_inv_1 - total_demand_1) and 'Inventory_Difference' in summary_1.columns
    feature_2_ok = (inv_diff_2 == effective_inv_2 - total_demand_2) and 'Inventory_Difference' in summary_2.columns
    removal_ok = ('Out_of_Stock_Warning' not in summary_1.columns) and ('Out_of_Stock_Warning' not in summary_2.columns)
    
    print(f"Positive difference calculation: {'PASS' if feature_1_ok else 'FAIL'}")
    print(f"Negative difference calculation: {'PASS' if feature_2_ok else 'FAIL'}")
    print(f"Out_of_Stock_Warning removal: {'PASS' if removal_ok else 'FAIL'}")
    print(f"Overall implementation: {'SUCCESS' if (feature_1_ok and feature_2_ok and removal_ok) else 'FAILED'}")
    
    return summary_1, summary_2

if __name__ == "__main__":
    test_final()