import pandas as pd
from promo_calculator import generate_summary, Config

def test_simple():
    # Test case 1: Effective_Inventory > Total_Demand
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
    
    # Test case 2: Effective_Inventory < Total_Demand
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
    
    print("=== Test Results ===")
    
    # Test case 1
    summary_1 = generate_summary(test_data_1, cfg)
    effective_inv_1 = summary_1["Effective_Inventory"].iloc[0]
    total_demand_1 = summary_1["Total_Demand"].iloc[0]
    status_1 = summary_1["Enhanced_Inventory_Status"].iloc[0]
    
    print(f"Test 1 - Effective_Inventory: {effective_inv_1}, Total_Demand: {total_demand_1}")
    print(f"Status contains sufficient stock: {'Yes' if '庫存足夠' in status_1 else 'No'}")
    print(f"Logic correct: {'Yes' if (effective_inv_1 >= total_demand_1 and '庫存足夠' in status_1) else 'No'}")
    
    # Test case 2
    summary_2 = generate_summary(test_data_2, cfg)
    effective_inv_2 = summary_2["Effective_Inventory"].iloc[0]
    total_demand_2 = summary_2["Total_Demand"].iloc[0]
    status_2 = summary_2["Enhanced_Inventory_Status"].iloc[0]
    
    print(f"\nTest 2 - Effective_Inventory: {effective_inv_2}, Total_Demand: {total_demand_2}")
    print(f"Status contains insufficient stock: {'Yes' if '庫存不足夠' in status_2 else 'No'}")
    print(f"Logic correct: {'Yes' if (effective_inv_2 < total_demand_2 and '庫存不足夠' in status_2) else 'No'}")
    
    print(f"\n=== Fix Verification ===")
    print(f"Test 1 Passed: {effective_inv_1 >= total_demand_1 and '庫存足夠' in status_1}")
    print(f"Test 2 Passed: {effective_inv_2 < total_demand_2 and '庫存不足夠' in status_2}")
    print(f"Overall Fix: {'SUCCESS' if (effective_inv_1 >= total_demand_1 and '庫存足夠' in status_1 and effective_inv_2 < total_demand_2 and '庫存不足夠' in status_2) else 'FAILED'}")

if __name__ == "__main__":
    test_simple()