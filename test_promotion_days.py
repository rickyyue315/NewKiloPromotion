#!/usr/bin/env python3
"""
測試 Promotion Days 對 Suggested_DN_Qty 計算的影響

測試場景：
1. Promotion Days > 4 時，Suggested_DN_Qty 的上限為 50 件
2. Promotion Days <= 4 時，Suggested_DN_Qty 無上限
3. 確保 Suggested_DN_Qty 仍需參考 MOQ 為倍數
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path to import promo_calculator
sys.path.append(str(Path(__file__).parent))

from promo_calculator import Config, calculate_demand, merge_data, prepare_file_a, prepare_file_b


def create_test_data():
    """創建測試數據"""
    # File A 測試數據
    test_data_a = pd.DataFrame({
        "Article": ["TEST001", "TEST001", "TEST002", "TEST002", "TEST003", "TEST003"],
        "Site": ["D001", "HA01", "D001", "HA01", "D001", "HA01"],
        "RP Type": ["RF", "ND", "RF", "ND", "RF", "ND"],
        "SaSa Net Stock": ["200", "50", "200", "50", "200", "50"],
        "Pending Received": ["10", "5", "10", "5", "10", "5"],
        "Safety Stock": ["20", "10", "20", "10", "20", "10"],
        "Last Month Sold Qty": ["100", "30", "100", "30", "100", "30"],
        "MOQ": ["12", "12", "6", "6", "2", "2"],
        "Supply source": ["2", "2", "2", "2", "2", "2"],
    })
    
    # File B Sheet1 測試數據
    test_data_b1 = pd.DataFrame({
        "Group No.": ["G001", "G002", "G003"],
        "Article": ["TEST001", "TEST002", "TEST003"],
        "SKU Target": ["100", "100", "100"],
        "Target Type": ["ALL", "ALL", "ALL"],
        "Promotion Days": ["5", "3", "5"],  # 兩個 >4，一個 <=4
        "Target Cover Days": ["7", "7", "7"],
    })
    
    # File B Sheet2 測試數據
    test_data_b2 = pd.DataFrame({
        "Site": ["D001", "HA01"],
        "Shop Target(HK)": ["0.5", "0.5"],
        "Shop Target(MO)": ["0.3", "0.3"],
        "Shop Target(ALL)": ["1.0", "1.0"],
    })
    
    return test_data_a, test_data_b1, test_data_b2


def test_promotion_days_logic():
    """Test Promotion Days logic"""
    print("=" * 60)
    print("Testing Promotion Days impact on Suggested_DN_Qty calculation")
    print("=" * 60)
    
    cfg = Config()
    test_data_a, test_data_b1, test_data_b2 = create_test_data()
    
    # Prepare data
    df_a_clean, _ = prepare_file_a(test_data_a, cfg)
    df_b1, df_b2, _ = prepare_file_b(test_data_b1, test_data_b2, cfg)
    
    # Merge data
    merged, _ = merge_data(df_a_clean, df_b1, df_b2, cfg)
    
    # Calculate demand
    detail = calculate_demand(merged, cfg, lead_time=7)
    
    # Display results
    print("\nTest Results:")
    print("-" * 60)
    
    for _, row in detail.iterrows():
        article = row["Article"]
        site = row["Site"]
        rp_type = row["RP_Type"]
        promotion_days = row["Promotion_Days"]
        moq = row["MOQ"]
        site_promo_demand = row["Site_Promo_Demand"]
        suggested_dn_qty = row["Suggested_DN_Qty"]
        
        print(f"Article: {article}, Site: {site}, RP_Type: {rp_type}")
        print(f"  Promotion Days: {promotion_days}")
        print(f"  MOQ: {moq}")
        print(f"  Site Promo Demand: {site_promo_demand:.2f}")
        print(f"  Suggested DN Qty: {suggested_dn_qty}")
        
        # Get Suggested_Dispatch_Qty for comparison
        suggested_dispatch_qty = row.get("Suggested_Dispatch_Qty", 0)
        try:
            dispatch_qty = float(suggested_dispatch_qty) if pd.notna(suggested_dispatch_qty) else 0
        except (TypeError, ValueError):
            dispatch_qty = 0.0
        
        print(f"  Suggested Dispatch Qty: {dispatch_qty}")
        
        # Verify logic based on user feedback
        if promotion_days > 4:
            if dispatch_qty <= 50:
                expected_dn_qty = dispatch_qty
                if suggested_dn_qty == expected_dn_qty:
                    print(f"  [OK] CORRECT: Promotion Days > 4, Dispatch Qty <= 50, DN Qty = Dispatch Qty")
                else:
                    print(f"  [X] ERROR: Promotion Days > 4, Dispatch Qty <= 50, DN Qty should equal Dispatch Qty")
            else:
                expected_dn_qty = 50
                if suggested_dn_qty <= expected_dn_qty:
                    print(f"  [OK] CORRECT: Promotion Days > 4, Dispatch Qty > 50, DN Qty capped at 50")
                else:
                    print(f"  [X] ERROR: Promotion Days > 4, Dispatch Qty > 50, DN Qty should be capped at 50")
        else:
            expected_dn_qty = dispatch_qty
            if suggested_dn_qty == expected_dn_qty:
                print(f"  [OK] CORRECT: Promotion Days <= 4, DN Qty = Dispatch Qty")
            else:
                print(f"  [X] ERROR: Promotion Days <= 4, DN Qty should equal Dispatch Qty")
        
        # Verify MOQ multiple
        if suggested_dn_qty > 0 and moq > 0:
            if suggested_dn_qty % moq == 0:
                print(f"  [OK] CORRECT: Suggested DN Qty is a multiple of MOQ")
            else:
                print(f"  [X] ERROR: Suggested DN Qty is not a multiple of MOQ")
        
        print("-" * 60)
    
    # Special test: Create a scenario requiring large replenishment
    print("\nSpecial Test: Large Replenishment Scenario")
    print("-" * 60)
    
    # Create test data requiring large replenishment
    large_demand_data_a = pd.DataFrame({
        "Article": ["LARGE001"],
        "Site": ["HA01"],
        "RP Type": ["ND"],
        "SaSa Net Stock": ["0"],
        "Pending Received": ["0"],
        "Safety Stock": ["0"],
        "Last Month Sold Qty": ["0"],
        "MOQ": ["10"],
        "Supply source": ["2"],
    })
    
    large_demand_data_b1 = pd.DataFrame({
        "Group No.": ["G003"],
        "Article": ["LARGE001"],
        "SKU Target": ["200"],  # 大目標
        "Target Type": ["ALL"],
        "Promotion Days": ["5"],  # > 4，應有上限
        "Target Cover Days": ["7"],
    })
    
    df_a_large, _ = prepare_file_a(large_demand_data_a, cfg)
    df_b1_large, df_b2_large, _ = prepare_file_b(large_demand_data_b1, test_data_b2, cfg)
    
    merged_large, _ = merge_data(df_a_large, df_b1_large, df_b2_large, cfg)
    detail_large = calculate_demand(merged_large, cfg, lead_time=7)
    
    for _, row in detail_large.iterrows():
        article = row["Article"]
        site = row["Site"]
        promotion_days = row["Promotion_Days"]
        moq = row["MOQ"]
        site_promo_demand = row["Site_Promo_Demand"]
        suggested_dn_qty = row["Suggested_DN_Qty"]
        
        print(f"Article: {article}, Site: {site}")
        print(f"  Promotion Days: {promotion_days}")
        print(f"  MOQ: {moq}")
        print(f"  Site Promo Demand: {site_promo_demand:.2f}")
        print(f"  Suggested DN Qty: {suggested_dn_qty}")
        
        # 計算理論上無上限的值
        theoretical_qty = int((site_promo_demand // moq + (1 if site_promo_demand % moq > 0 else 0)) * moq)
        
        if promotion_days > 4:
            if suggested_dn_qty == 50:
                print(f"  [OK] CORRECT: Promotion Days > 4, limited to 50 even with high demand")
            else:
                print(f"  [X] ERROR: Promotion Days > 4 should be limited to 50, actual is {suggested_dn_qty}")
        
        print(f"  Theoretical unlimited value: {theoretical_qty}")
        print("-" * 60)
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_promotion_days_logic()