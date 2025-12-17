import pandas as pd
from promo_calculator import generate_summary, Config

def test_inventory_logic():
    """Test inventory logic fix"""
    
    # Test case 1: Effective_Inventory > Total_Demand (should show "庫存足夠")
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
    
    # Test case 2: Effective_Inventory < Total_Demand (should show "庫存不足夠")
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
    
    print("=== Test Inventory Logic Fix ===")
    
    # Test case 1
    try:
        summary_1 = generate_summary(test_data_1, cfg)
        effective_inv_1 = summary_1["Effective_Inventory"].iloc[0]
        total_demand_1 = summary_1["Total_Demand"].iloc[0]
        status_1 = summary_1["Enhanced_Inventory_Status"].iloc[0]
        
        print(f"\nTest Case 1:")
        print(f"Effective_Inventory: {effective_inv_1}")
        print(f"Total_Demand: {total_demand_1}")
        print(f"Enhanced_Inventory_Status: {status_1}")
        print(f"Expected: Stock sufficient (because {effective_inv_1} >= {total_demand_1})")
        print(f"Result: {'✓ Correct' if '庫存足夠' in status_1 else '✗ Wrong'}")
        
    except Exception as e:
        print(f"Test Case 1 Error: {e}")
    
    # Test case 2
    try:
        summary_2 = generate_summary(test_data_2, cfg)
        effective_inv_2 = summary_2["Effective_Inventory"].iloc[0]
        total_demand_2 = summary_2["Total_Demand"].iloc[0]
        status_2 = summary_2["Enhanced_Inventory_Status"].iloc[0]
        
        print(f"\nTest Case 2:")
        print(f"Effective_Inventory: {effective_inv_2}")
        print(f"Total_Demand: {total_demand_2}")
        print(f"Enhanced_Inventory_Status: {status_2}")
        print(f"Expected: Stock insufficient (because {effective_inv_2} < {total_demand_2})")
        print(f"Result: {'✓ Correct' if '庫存不足夠' in status_2 else '✗ Wrong'}")
        
    except Exception as e:
        print(f"Test Case 2 Error: {e}")

if __name__ == "__main__":
    test_inventory_logic()