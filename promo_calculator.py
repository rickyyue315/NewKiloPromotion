import math
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import pandas as pd


class Config:
    """
    Central configuration for calculation behavior.
    Adjust here instead of scattering "magic numbers".
    """

    # For Daily Sales Rate
    DAYS_IN_MONTH_FOR_RATE: int = 30

    # Default Target Cover Days when not provided in File B Sheet1
    DEFAULT_TARGET_COVER_DAYS: int = 7

    # Lead time default (can be overridden by CLI arg or UI)
    DEFAULT_LEAD_TIME: int = 7

    # Max cap for Last Month Sold Qty
    LAST_MONTH_SOLD_CAP: int = 100000

    # If True: Net_Demand_for_Dispatch never uses negatives
    USE_NEGATIVE_NET_FOR_DISPATCH: bool = False

    # MOQ behavior when missing / invalid
    # "zero" = treat as 0 (no dispatch), "one" = assume 1
    MISSING_MOQ_POLICY: str = "zero"

    # RP Type that should be calculated for dispatch
    DISPATCH_RP_TYPE: str = "RF"

    # Column names for File A (Sheet: Data)
    COL_A_ARTICLE: str = "Article"
    COL_A_SITE: str = "Site"
    COL_A_RP_TYPE: str = "RP Type"
    COL_A_NET_STOCK: str = "SaSa Net Stock"
    COL_A_PENDING: str = "Pending Received"
    COL_A_SAFETY: str = "Safety Stock"
    COL_A_LAST_MONTH_SOLD: str = "Last Month Sold Qty"
    COL_A_MOQ: str = "MOQ"
    COL_A_SUPPLY_SOURCE: str = "Supply source"
    COL_A_IN_QLTY: str = "In Quality Insp."
    COL_A_BLOCKED: str = "Blocked"

    # Column names for File B Sheet1
    COL_B1_GROUP_NO: str = "Group No."
    COL_B1_ARTICLE: str = "Article"
    COL_B1_SKU_TARGET: str = "SKU Target"
    COL_B1_TARGET_TYPE: str = "Target Type"
    COL_B1_PROMO_DAYS: str = "Promotion Days"
    COL_B1_TARGET_COVER_DAYS: str = "Target Cover Days"

    # Column names for File B Sheet2
    COL_B2_SITE: str = "Site"
    COL_B2_HK: str = "Shop Target(HK)"
    COL_B2_MO: str = "Shop Target(MO)"
    COL_B2_ALL: str = "Shop Target(ALL)"

    # D001 DC site code
    DC_SITE_CODE: str = "D001"


def read_input_files(
    file_a_path: Path,
    file_b_path: Path,
    config: Config,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load:
    - File A: main inventory & sales (Sheet: Data or Sheet 1)
    - File B: Sheet1 (promo SKU list), Sheet2 (site target %)

    Returns:
    (df_a, df_b1, df_b2)
    """
    # File A - 直接讀取 "Sheet1" 工作表
    try:
        df_a = pd.read_excel(file_a_path, sheet_name="Sheet1", dtype=str)
    except ValueError:
        # 如果失敗，列出所有可用的工作表名稱
        xls_a = pd.ExcelFile(file_a_path)
        available_sheets = xls_a.sheet_names
        raise ValueError(
            f"File A missing required sheet 'Sheet1'. "
            f"Available sheets: {available_sheets}"
        )

    # File B
    xls_b = pd.ExcelFile(file_b_path)
    df_b1 = pd.read_excel(xls_b, sheet_name="Sheet 1", dtype=str)
    df_b2 = pd.read_excel(xls_b, sheet_name="Sheet 2", dtype=str)

    return df_a, df_b1, df_b2


def to_numeric(series: pd.Series, col_name: str, warnings: List[str]) -> pd.Series:
    """
    Convert to numeric, coerce errors to 0, negative to 0.
    """
    s = pd.to_numeric(series, errors="coerce").fillna(0)
    negatives = (s < 0).sum()
    if negatives > 0:
        warnings.append(f"{col_name}: {negatives} negative values set to 0")
        s = s.clip(lower=0)
    return s


def prepare_file_a(df_a_raw: pd.DataFrame, config: Config) -> Tuple[pd.DataFrame, List[str]]:
    """
    Clean and normalize File A data.

    Output columns (at least):
    - Article
    - Site
    - RP_Type
    - SaSa_Net_Stock
    - Pending_Received
    - Safety_Stock
    - Last_Month_Sold_Qty_capped
    - MOQ
    - Supply_source
    - In_Quality_Insp (optional, default 0)
    - Blocked (optional, default 0)
    """
    warnings: List[str] = []

    df = df_a_raw.copy()

    # Basic column existence checks
    required_cols = [
        config.COL_A_ARTICLE,
        config.COL_A_SITE,
        config.COL_A_RP_TYPE,
        config.COL_A_NET_STOCK,
        config.COL_A_PENDING,
        config.COL_A_SAFETY,
        config.COL_A_LAST_MONTH_SOLD,
        config.COL_A_MOQ,
        config.COL_A_SUPPLY_SOURCE,
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"File A missing required columns: {missing}")

    # Trim Article, Site
    df[config.COL_A_ARTICLE] = df[config.COL_A_ARTICLE].astype(str).str.strip()
    df[config.COL_A_SITE] = df[config.COL_A_SITE].astype(str).str.strip().str.upper()

    # Normalize numeric columns
    df["SaSa_Net_Stock"] = to_numeric(df[config.COL_A_NET_STOCK], config.COL_A_NET_STOCK, warnings)
    df["Pending_Received"] = to_numeric(df[config.COL_A_PENDING], config.COL_A_PENDING, warnings)
    df["Safety_Stock"] = to_numeric(df[config.COL_A_SAFETY], config.COL_A_SAFETY, warnings)
    df["Last_Month_Sold_Qty"] = to_numeric(
        df[config.COL_A_LAST_MONTH_SOLD], config.COL_A_LAST_MONTH_SOLD, warnings
    )
    df["MOQ"] = to_numeric(df[config.COL_A_MOQ], config.COL_A_MOQ, warnings)

    # Supply source: normalize robustly; keep as numeric (float) to avoid NaN→int issues during apply()
    supply_raw = pd.to_numeric(df[config.COL_A_SUPPLY_SOURCE], errors="coerce")
    supply_raw = supply_raw.fillna(0)
    # Negative or weird values → 0
    supply_raw = supply_raw.clip(lower=0)
    df["Supply_source"] = supply_raw

    # In Quality Insp, Blocked as optional
    if config.COL_A_IN_QLTY in df.columns:
        df["In_Quality_Insp"] = to_numeric(df[config.COL_A_IN_QLTY], config.COL_A_IN_QLTY, warnings)
    else:
        df["In_Quality_Insp"] = 0

    if config.COL_A_BLOCKED in df.columns:
        df["Blocked"] = to_numeric(df[config.COL_A_BLOCKED], config.COL_A_BLOCKED, warnings)
    else:
        df["Blocked"] = 0

    # Cap Last Month Sold Qty
    capped_mask = df["Last_Month_Sold_Qty"] > config.LAST_MONTH_SOLD_CAP
    capped_count = int(capped_mask.sum())
    if capped_count > 0:
        df.loc[capped_mask, "Last_Month_Sold_Qty"] = config.LAST_MONTH_SOLD_CAP
        warnings.append(
            f"Last Month Sold Qty: {capped_count} values capped at {config.LAST_MONTH_SOLD_CAP}"
        )

    df["Last_Month_Sold_Qty_capped"] = df["Last_Month_Sold_Qty"]

    # RP Type normalization
    df["RP_Type"] = df[config.COL_A_RP_TYPE].fillna("").astype(str).str.strip().str.upper()

    # Deduplicate by (Article, Site): sum numeric fields if duplicates
    key_cols = [config.COL_A_ARTICLE, config.COL_A_SITE]
    group_fields_sum = [
        "SaSa_Net_Stock",
        "Pending_Received",
        "Safety_Stock",
        "Last_Month_Sold_Qty",
        "Last_Month_Sold_Qty_capped",
        "MOQ",
        "In_Quality_Insp",
        "Blocked",
    ]
    # For RP_Type, Supply_source: take the first non-null; in real system use stricter validation.
    if df.duplicated(key_cols).any():
        warnings.append("Duplicates found in File A on (Article, Site); aggregated by sum for numerics.")
        agg_map = {col: "sum" for col in group_fields_sum}
        agg_map["RP_Type"] = "first"
        agg_map["Supply_source"] = "first"
        df = (
            df.groupby(key_cols, as_index=False)
            .agg(agg_map)
        )

    # Rename for unified downstream schema
    df = df.rename(
        columns={
            config.COL_A_ARTICLE: "Article",
            config.COL_A_SITE: "Site",
        }
    )

    return df, warnings


def prepare_file_b(
    df_b1_raw: pd.DataFrame,
    df_b2_raw: pd.DataFrame,
    config: Config,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Normalize and validate File B Sheet1 and Sheet2.

    Sheet1 output columns:
    - Group_No
    - Article
    - SKU_Target
    - Target_Type
    - Promo_Target_Cover_Days

    Sheet2 output columns:
    - Site
    - Pct_HK
    - Pct_MO
    - Pct_ALL
    """
    warnings: List[str] = []

    # Sheet 1 checks
    required_b1 = [
        config.COL_B1_GROUP_NO,
        config.COL_B1_ARTICLE,
        config.COL_B1_SKU_TARGET,
    ]
    missing_b1 = [c for c in required_b1 if c not in df_b1_raw.columns]
    if missing_b1:
        raise ValueError(f"File B Sheet1 missing required columns: {missing_b1}")

    df_b1 = df_b1_raw.copy()
    df_b1[config.COL_B1_ARTICLE] = df_b1[config.COL_B1_ARTICLE].astype(str).str.strip()
    df_b1[config.COL_B1_GROUP_NO] = df_b1[config.COL_B1_GROUP_NO].astype(str).str.strip()

    df_b1["SKU_Target"] = to_numeric(df_b1[config.COL_B1_SKU_TARGET], config.COL_B1_SKU_TARGET, warnings)

    if config.COL_B1_TARGET_TYPE in df_b1.columns:
        df_b1["Target_Type"] = df_b1[config.COL_B1_TARGET_TYPE].astype(str).str.strip().str.upper()
    else:
        df_b1["Target_Type"] = "ALL"

    # Target Cover Days (optional)
    if config.COL_B1_TARGET_COVER_DAYS in df_b1.columns:
        df_b1["Promo_Target_Cover_Days"] = to_numeric(
            df_b1[config.COL_B1_TARGET_COVER_DAYS],
            config.COL_B1_TARGET_COVER_DAYS,
            warnings,
        )
        # zero treated as "not provided"
        df_b1.loc[df_b1["Promo_Target_Cover_Days"] <= 0, "Promo_Target_Cover_Days"] = 0
    else:
        df_b1["Promo_Target_Cover_Days"] = 0

    df_b1 = df_b1.rename(
        columns={
            config.COL_B1_GROUP_NO: "Group_No",
            config.COL_B1_ARTICLE: "Article",
        }
    )

    # Sheet 2 checks
    required_b2 = [
        config.COL_B2_SITE,
        config.COL_B2_HK,
        config.COL_B2_MO,
        config.COL_B2_ALL,
    ]
    missing_b2 = [c for c in required_b2 if c not in df_b2_raw.columns]
    if missing_b2:
        raise ValueError(f"File B Sheet2 missing required columns: {missing_b2}")

    df_b2 = df_b2_raw.copy()
    df_b2[config.COL_B2_SITE] = df_b2[config.COL_B2_SITE].astype(str).str.strip().str.upper()

    def pct_col(col: str) -> pd.Series:
        s = pd.to_numeric(df_b2[col], errors="coerce").fillna(0.0)
        # Accept both 0-1 and 0-100; treat >1 as percentage
        mask_pct = s > 1
        if mask_pct.any():
            s.loc[mask_pct] = s.loc[mask_pct] / 100.0
        return s

    df_b2["Pct_HK"] = pct_col(config.COL_B2_HK)
    df_b2["Pct_MO"] = pct_col(config.COL_B2_MO)
    df_b2["Pct_ALL"] = pct_col(config.COL_B2_ALL)

    df_b2 = df_b2.rename(columns={config.COL_B2_SITE: "Site"})

    return df_b1, df_b2, warnings


def merge_data(
    df_a: pd.DataFrame,
    df_b1: pd.DataFrame,
    df_b2: pd.DataFrame,
    config: Config,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Merge A with promotion definitions and site target percentages to form a unified working dataset.

    Resulting columns include:
    - Article, Site
    - RP_Type, SaSa_Net_Stock, Pending_Received, Safety_Stock, Last_Month_Sold_Qty_capped, MOQ, Supply_source
    - Group_No, SKU_Target, Target_Type, Promo_Target_Cover_Days
    - Site_Target_%
    - Is_Promo_SKU
    
    Returns: (merged_df, warnings)
    """
    warnings: List[str] = []
    
    # Track File A SKUs
    articles_in_a = set(df_a["Article"].unique())
    articles_in_b1 = set(df_b1["Article"].unique())
    
    # Diagnostic: Check for Article overlap
    matched_articles = articles_in_a.intersection(articles_in_b1)
    unmatched_in_a = articles_in_a - articles_in_b1
    unmatched_in_b1 = articles_in_b1 - articles_in_a
    
    if not matched_articles:
        warnings.append(
            f"⚠️ CRITICAL: NO Articles from File A matched with File B Sheet1! "
            f"File A has {len(articles_in_a)} unique Articles, "
            f"File B Sheet1 has {len(articles_in_b1)} unique Articles. "
            f"This means NO promotion targets will be applied."
        )
    else:
        warnings.append(
            f"✓ Article match summary: {len(matched_articles)} matched, "
            f"{len(unmatched_in_a)} in File A only, "
            f"{len(unmatched_in_b1)} in File B only."
        )
    
    if unmatched_in_a:
        warnings.append(
            f"Articles in File A but not in File B (no promo targets): {sorted(list(unmatched_in_a))[:10]}"
        )
    if unmatched_in_b1:
        warnings.append(
            f"Articles in File B but not in File A (unused promo targets): {sorted(list(unmatched_in_b1))}"
        )
    
    # Merge promo SKU info by Article (many sites share SKU)
    df = df_a.merge(
        df_b1[
            [
                "Group_No",
                "Article",
                "SKU_Target",
                "Target_Type",
                "Promo_Target_Cover_Days",
            ]
        ],
        on="Article",
        how="left",
    )

    # Merge site target by Site
    df = df.merge(
        df_b2[["Site", "Pct_HK", "Pct_MO", "Pct_ALL"]],
        on="Site",
        how="left",
    )

    # Determine Site_Target_% based on Target_Type
    def pick_site_target_pct(row) -> float:
        # Robust against non-string / NaN values
        raw_type = row.get("Target_Type")
        t = str(raw_type).upper() if raw_type is not None else ""
        if t == "HK":
            return float(row.get("Pct_HK") or 0)
        if t == "MO":
            return float(row.get("Pct_MO") or 0)
        # Default / ALL / unexpected values
        return float(row.get("Pct_ALL") or 0)

    df["Site_Target_%"] = df.apply(pick_site_target_pct, axis=1)

    # Determine promo flag: must have SKU_Target > 0 and Site_Target_% > 0
    df["Is_Promo_SKU"] = (df["SKU_Target"].fillna(0) > 0) & (df["Site_Target_%"].fillna(0) > 0)
    
    # Diagnostic: Count promo SKUs
    promo_count = df["Is_Promo_SKU"].sum()
    total_rows = len(df)
    warnings.append(
        f"Promo SKU detection: {promo_count} out of {total_rows} rows flagged as promotion SKUs"
    )

    return df, warnings


def calculate_demand(
    df: pd.DataFrame,
    config: Config,
    lead_time: Optional[int] = None,
) -> pd.DataFrame:
    """
    Apply the core demand and dispatch logic to the merged dataset.
    """
    lead = config.DEFAULT_LEAD_TIME if lead_time is None else int(lead_time)

    out = df.copy()

    # Daily_Sales_Rate
    out["Daily_Sales_Rate"] = out["Last_Month_Sold_Qty_capped"] / float(config.DAYS_IN_MONTH_FOR_RATE)

    # Effective_Target_Cover_Days
    out["Effective_Target_Cover_Days"] = out["Promo_Target_Cover_Days"]
    out.loc[out["Effective_Target_Cover_Days"] <= 0, "Effective_Target_Cover_Days"] = (
        config.DEFAULT_TARGET_COVER_DAYS
    )

    # Base_Demand
    out["Base_Demand"] = out["Daily_Sales_Rate"] * (
        out["Effective_Target_Cover_Days"] + lead
    )

    # Promotion Demand
    out["Site_Promo_Demand"] = 0.0
    promo_mask = out["Is_Promo_SKU"]
    out.loc[promo_mask, "Site_Promo_Demand"] = (
        out.loc[promo_mask, "SKU_Target"] * out.loc[promo_mask, "Site_Target_%"]
    )

    # Total_Demand
    out["Total_Demand"] = out["Base_Demand"] + out["Site_Promo_Demand"]

    # Net_Demand_raw (without Safety Stock)
    out["Net_Demand_raw"] = (
        out["Total_Demand"]
        - (out["SaSa_Net_Stock"] + out["Pending_Received"])
    )

    # Net_Demand_for_Dispatch
    if config.USE_NEGATIVE_NET_FOR_DISPATCH:
        out["Net_Demand_for_Dispatch"] = out["Net_Demand_raw"]
    else:
        out["Net_Demand_for_Dispatch"] = out["Net_Demand_raw"].clip(lower=0)

    # MOQ policy
    if config.MISSING_MOQ_POLICY == "one":
        out.loc[out["MOQ"] <= 0, "MOQ"] = 1
    else:
        # "zero": keep 0, which will result in no dispatch
        pass

    # Suggested Dispatch Qty
    def compute_suggested_dispatch(row) -> int:
        rp = (row.get("RP_Type") or "").upper()
        if rp != config.DISPATCH_RP_TYPE:
            return 0

        # Net demand: safe numeric
        net_raw = row.get("Net_Demand_for_Dispatch", 0)
        try:
            net = float(net_raw)
        except (TypeError, ValueError):
            net = 0.0
        if not pd.notna(net) or net <= 0:
            return 0

        # MOQ: safe numeric
        moq_raw = row.get("MOQ", 0)
        try:
            moq = float(moq_raw)
        except (TypeError, ValueError):
            moq = 0.0
        if not pd.notna(moq) or moq <= 0:
            # no valid MOQ, follow policy: here treat as no dispatch
            return 0

        base_qty = max(net, moq)
        # 保證不因 NaN 導致錯誤；ceil 結果若非有限數字則視為 0
        try:
            result = math.ceil(base_qty / moq) * moq
        except Exception:
            return 0
        if not pd.notna(result) or result < 0:
            return 0
        return int(result)

    out["Suggested_Dispatch_Qty"] = out.apply(compute_suggested_dispatch, axis=1)

    # Dispatch_Type
    def determine_dispatch_type(row) -> str:
        site = (row.get("Site") or "").upper()
        rp = (row.get("RP_Type") or "").upper()

        # Supply_source might be float/NaN; convert safely
        raw_supply = row.get("Supply_source", 0)
        try:
            supply = int(raw_supply) if pd.notna(raw_supply) else 0
        except (TypeError, ValueError):
            supply = 0

        if site == config.DC_SITE_CODE:
            return "D001"
        if rp == "ND":
            return "ND"
        if supply in (1, 4):
            return "Buyer需要訂貨"
        if supply == 2:
            return "需生成 DN"
        return "N/A"

    out["Dispatch_Type"] = out.apply(determine_dispatch_type, axis=1)

    return out


def generate_summary(
    detail: pd.DataFrame,
    config: Config,
) -> pd.DataFrame:
    """
    Generate summary report per (Group_No, Article) as described:

    - For non-D001 sites: aggregate Total_Demand, SaSa_Net_Stock, Pending_Received, Suggested_Dispatch_Qty.
    - For D001: show DC stock metrics.
    - Out_of_Stock_Warning per SKU based on rules.
    """
    # Separate D001 and non-D001
    non_dc = detail[detail["Site"] != config.DC_SITE_CODE]
    dc = detail[detail["Site"] == config.DC_SITE_CODE]

    # Aggregate non-DC
    grp_keys = ["Group_No", "Article"]

    agg_non_dc = (
        non_dc.groupby(grp_keys, as_index=False)
        .agg(
            Total_Demand=("Total_Demand", "sum"),
            Total_Stock=("SaSa_Net_Stock", "sum"),
            Total_Pending=("Pending_Received", "sum"),
            Total_Dispatch=("Suggested_Dispatch_Qty", "sum"),
        )
    )
    agg_non_dc["Total_Stock_Available"] = agg_non_dc["Total_Stock"] + agg_non_dc["Total_Pending"]

    # D001 info: assume at most one row per (Article) for DC; if multiple, sum
    dc_agg = (
        dc.groupby("Article", as_index=False)
        .agg(
            D001_SaSa_Net_Stock=("SaSa_Net_Stock", "sum"),
            D001_In_Quality_Insp=("In_Quality_Insp", "sum"),
            D001_Blocked=("Blocked", "sum"),
            D001_Pending_Received=("Pending_Received", "sum"),
        )
    )

    # Merge D001 info into summary (on Article)
    summary = agg_non_dc.merge(dc_agg, on="Article", how="left")

    # Fill NaN for D001 fields with 0 for calculations
    for col in [
        "D001_SaSa_Net_Stock",
        "D001_In_Quality_Insp",
        "D001_Blocked",
        "D001_Pending_Received",
    ]:
        if col in summary.columns:
            summary[col] = summary[col].fillna(0)

    # Out_of_Stock_Warning
    warnings = []
    for _, row in summary.iterrows():
        total_dispatch = row["Total_Dispatch"]
        dc_stock = row["D001_SaSa_Net_Stock"]
        total_demand = row["Total_Demand"]
        total_stock_avail = row["Total_Stock_Available"]

        if total_dispatch > dc_stock:
            warnings.append("D001 缺貨")
        elif total_demand > total_stock_avail:
            warnings.append("Y")
        else:
            warnings.append("N")

    summary["Out_of_Stock_Warning"] = warnings

    return summary


def export_to_excel(
    detail: pd.DataFrame,
    summary: pd.DataFrame,
    df_a_clean: pd.DataFrame,
    df_b1: pd.DataFrame,
    df_b2: pd.DataFrame,
    output_path: Path,
):
    """
    Export simplified views (remove intermediate/duplicated columns):

    - Final Order Report:
        Raw_A_Clean + Suggested_Dispatch_Qty, Dispatch_Type, SKU_Target, Site_Target_%, Total_Demand
        (Values instead of formulas for better usability)

    - Promo_Sheet1 / Promo_Sheet2:
        Keep as-is (reference configuration).

    - Detail_Calculation (SIMPLIFIED):
        Only final decision-useful fields:
        [
            "Group_No",
            "Article",
            "Site",
            "RP_Type",
            "SaSa_Net_Stock",
            "Pending_Received",
            "Safety_Stock",
            "SKU_Target",
            "Site_Target_%",
            "Is_Promo_SKU",
            "Total_Demand",
            "Suggested_Dispatch_Qty",
            "Dispatch_Type",
        ]
        (Columns missing in data will be skipped safely.)

    - Summary_Report (SIMPLIFIED):
        Only aggregated decision fields:
        [
            "Group_No",
            "Article",
            "Total_Demand",
            "Total_Stock_Available",
            "Total_Stock",
            "Total_Pending",
            "Total_Dispatch",
            "D001_SaSa_Net_Stock",
            "Out_of_Stock_Warning",
        ]
        (Columns missing in data will be skipped safely.)
    """
    # Create Final Order Report with additional columns
    # First, merge df_a_clean with the calculated columns from detail
    merge_keys = ["Article", "Site"]
    
    # Get the additional columns from detail
    additional_cols = ["Suggested_Dispatch_Qty", "Dispatch_Type", "SKU_Target", "Site_Target_%", "Total_Demand"]
    additional_data = detail[merge_keys + additional_cols].copy()
    
    # Remove duplicates in additional_data to ensure clean merge
    additional_data = additional_data.drop_duplicates(subset=merge_keys, keep='first')
    
    # Merge df_a_clean with additional columns
    df_final_order_report = df_a_clean.merge(
        additional_data,
        on=merge_keys,
        how="left"
    )
    
    # Define keep-lists for simplified outputs
    detail_keep_cols = [
        "Group_No",
        "Article",
        "Site",
        "RP_Type",
        "SaSa_Net_Stock",
        "Pending_Received",
        "Safety_Stock",
        "SKU_Target",
        "Site_Target_%",
        "Is_Promo_SKU",
        "Total_Demand",
        "Suggested_Dispatch_Qty",
        "Dispatch_Type",
    ]
    # Keep only existing columns, avoid KeyError
    detail_simple_cols = [c for c in detail_keep_cols if c in detail.columns]
    detail_simple = detail[detail_simple_cols].copy()

    summary_keep_cols = [
        "Group_No",
        "Article",
        "Total_Demand",
        "Total_Stock_Available",
        "Total_Stock",
        "Total_Pending",
        "Total_Dispatch",
        "D001_SaSa_Net_Stock",
        "Out_of_Stock_Warning",
    ]
    summary_simple_cols = [c for c in summary_keep_cols if c in summary.columns]
    summary_simple = summary[summary_simple_cols].copy()

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        # Config sheets unchanged for traceability
        df_final_order_report.to_excel(writer, sheet_name="Final Order Report", index=False)
        df_b1.to_excel(writer, sheet_name="Promo_Sheet1", index=False)
        df_b2.to_excel(writer, sheet_name="Promo_Sheet2", index=False)

        # Simplified views for business users
        detail_simple.to_excel(writer, sheet_name="Detail_Calculation", index=False)
        summary_simple.to_excel(writer, sheet_name="Summary_Report", index=False)


def main(
    file_a: str = "Promotion Target File A.XLSX",
    file_b: str = "Promotion Target File B.xlsx",
    lead_time: Optional[int] = None,
    output: str = "Promotion_Planning_Result.xlsx",
):
    """
    Entry point for local run.

    Usage example (Windows cmd):
      python promo_calculator.py

    Or with parameters:
      python promo_calculator.py "Promotion Target File A.XLSX" "Promotion Target File B.xlsx" 10 "Result.xlsx"
    """
    cfg = Config()

    if lead_time is None and len(sys.argv) >= 4:
        try:
            lead_time = int(sys.argv[3])
        except ValueError:
            lead_time = cfg.DEFAULT_LEAD_TIME

    if lead_time is None:
        lead_time = cfg.DEFAULT_LEAD_TIME

    # CLI args parsing (simple)
    if len(sys.argv) >= 2:
        file_a = sys.argv[1]
    if len(sys.argv) >= 3:
        file_b = sys.argv[2]
    if len(sys.argv) >= 5:
        output = sys.argv[4]

    file_a_path = Path(file_a)
    file_b_path = Path(file_b)
    output_path = Path(output)

    df_a_raw, df_b1_raw, df_b2_raw = read_input_files(file_a_path, file_b_path, cfg)

    df_a_clean, warn_a = prepare_file_a(df_a_raw, cfg)
    df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, cfg)

    merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, cfg)
    detail = calculate_demand(merged, cfg, lead_time=lead_time)
    summary = generate_summary(detail, cfg)

    export_to_excel(detail, summary, df_a_clean, df_b1, df_b2, output_path)

    # Print warnings to stdout for user visibility
    all_warnings = warn_a + warn_b + warn_merge
    if all_warnings:
        print("\n=== WARNINGS ===")
        for w in all_warnings:
            print(f"- {w}")
        print("================\n")
    print(f"Calculation completed. Output written to: {output_path}")


if __name__ == "__main__":
    main()