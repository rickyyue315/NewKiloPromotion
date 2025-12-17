import pandas as pd
from promo_calculator import Config

def test_dispatch_type_logic():
    """直接測試 Dispatch_Type 邏輯"""
    
    config = Config()
    
    # 創建測試數據 - 模擬不同的情況
    test_cases = [
        # (Site, RP_Type, Supply_source, Suggested_DN_Qty, Expected_Type, Description)
        ('ND001', 'ND', 1, 0, '無須補貨', 'ND站點，Suggested_DN_Qty=0，Supply_source=1'),
        ('ND002', 'ND', 2, 0, '無須補貨', 'ND站點，Suggested_DN_Qty=0，Supply_source=2'),
        ('ND003', 'ND', 4, 0, '無須補貨', 'ND站點，Suggested_DN_Qty=0，Supply_source=4'),
        ('ND004', 'ND', 2, 0, '無須補貨', 'ND站點，Suggested_DN_Qty=0，Supply_source=2'),
        ('ND005', 'ND', 1, 10, '開PO', 'ND站點，Suggested_DN_Qty>0，Supply_source=1'),
        ('ND006', 'ND', 2, 20, '需生成 DN', 'ND站點，Suggested_DN_Qty>0，Supply_source=2'),
        ('ND007', 'ND', 4, 15, '開PO', 'ND站點，Suggested_DN_Qty>0，Supply_source=4'),
        ('D001', 'RF', 2, 0, 'D001', 'D001站點'),
        ('RF001', 'RF', 1, 0, 'Buyer需要訂貨', 'RF站點，Supply_source=1'),
        ('RF002', 'RF', 2, 0, '需生成 DN', 'RF站點，Supply_source=2'),
        ('RF003', 'RF', 4, 0, 'Buyer需要訂貨', 'RF站點，Supply_source=4'),
    ]
    
    print("Testing Dispatch_Type Logic:")
    print("=" * 80)
    
    for site, rp_type, supply_source, dn_qty, expected_type, description in test_cases:
        # 創建測試行
        test_row = {
            'Site': site,
            'RP_Type': rp_type,
            'Supply_source': supply_source,
            'Suggested_DN_Qty': dn_qty,
        }
        
        # 調用 determine_dispatch_type 函數邏輯
        result_type = determine_dispatch_type(test_row, config)
        
        # 檢查結果
        if result_type == expected_type:
            print(f"[PASS] {description}")
            print(f"   Result: {result_type} (Expected: {expected_type})")
        else:
            print(f"[FAIL] {description}")
            print(f"   Result: {result_type} (Expected: {expected_type})")
        
        print()

def determine_dispatch_type(row: dict, config: Config) -> str:
    """
    複製 promo_calculator.py 中的 determine_dispatch_type 邏輯
    """
    site = (row.get("Site") or "").upper()
    rp = (row.get("RP_Type") or "").upper()

    # Supply_source might be float/NaN; convert safely
    raw_supply = row.get("Supply_source", 0)
    try:
        supply = int(raw_supply) if pd.notna(raw_supply) else 0
    except (TypeError, ValueError):
        supply = 0

    # Check if Suggested_DN_Qty > 0 for ND sites
    suggested_dn_qty = row.get("Suggested_DN_Qty", 0)
    try:
        dn_qty = float(suggested_dn_qty) if pd.notna(suggested_dn_qty) else 0
    except (TypeError, ValueError):
        dn_qty = 0

    if site == config.DC_SITE_CODE:
        return "D001"
    if rp == "ND":
        if dn_qty > 0:
            # For ND sites with DN Qty > 0, use Supply_source to determine
            # 顯示"開PO"或"需生成 DN"而不是"ND"，因為Dispatch_Remark已有"ND派貨"提示
            if supply in (1, 4):
                return "開PO"
            elif supply == 2:
                return "需生成 DN"
            else:
                return "ND"
        else:
            # For ND sites with DN Qty = 0, show "無須補貨"
            return "無須補貨"
    if supply in (1, 4):
        return "Buyer需要訂貨"
    if supply == 2:
        return "需生成 DN"
    return "N/A"

if __name__ == "__main__":
    test_dispatch_type_logic()