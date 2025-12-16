import io
from pathlib import Path

import pandas as pd
import streamlit as st

# Import core logic from promo_calculator
# Ensure promo_calculator.py is in the same directory.
from promo_calculator import (
    Config,
    read_input_files,
    prepare_file_a,
    prepare_file_b,
    merge_data,
    calculate_demand,
    generate_summary,
    export_to_excel,
)


def run_app():
    st.set_page_config(
        page_title="Retail Promotion Demand & Dispatch Planner",
        layout="wide",
    )

    st.sidebar.title("Parameters")

    # Lead Time slider
    cfg = Config()
    lead_time = st.sidebar.slider(
        "Lead Time (Days)",
        min_value=0,
        max_value=60,
        value=cfg.DEFAULT_LEAD_TIME,
        step=1,
        help="Used in: Base Demand = Daily Sales Rate × (Target Cover Days + Lead Time).",
    )

    st.sidebar.markdown("---")
    with st.sidebar.expander("File Requirements (File A & B)", expanded=False):
        st.markdown(
            """
            - File A: Inventory & Sales
              - Sheet: Sheet1
              - Required columns:
                - Article, Site, RP Type, SaSa Net Stock, Pending Received,
                  Safety Stock, Last Month Sold Qty, MOQ, Supply source
            - File B:
              - Sheet 1: Group No., Article, SKU Target, Target Type, Target Cover Days
              - Sheet 2: Site, Shop Target(HK), Shop Target(MO), Shop Target(ALL)
            - Notes:
              - Site codes will be upper-cased.
              - Percent columns can be 0–1 or 0–100%.
              - Abnormal Last Month Sold Qty > 100,000 will be capped.
            """
        )

    st.title("零售推廣目標檢視及派貨系統")
    st.caption("Retail Promotion Demand & Dispatch Planning - Streamlit Interface")

    # File upload area
    col_a, col_b = st.columns(2)
    with col_a:
        file_a = st.file_uploader(
            "Upload File A (Promotion Target File A.XLSX)",
            type=["xlsx", "xls"],
            key="file_a",
        )
    with col_b:
        file_b = st.file_uploader(
            "Upload File B (Promotion Target File B.xlsx)",
            type=["xlsx", "xls"],
            key="file_b",
        )

    if not file_a or not file_b:
        st.info("請上載 File A 與 File B 後再按「開始分析」。")
        return

    # Start analysis button
    if st.button("開始分析 / Run Analysis", type="primary"):
        try:
            with st.spinner("Reading and validating input files..."):
                # Use in-memory bytes with pandas
                df_a_raw = pd.read_excel(file_a, sheet_name="Sheet1", dtype=str)

                xls_b = pd.ExcelFile(file_b)
                df_b1_raw = pd.read_excel(xls_b, sheet_name="Sheet 1", dtype=str)
                df_b2_raw = pd.read_excel(xls_b, sheet_name="Sheet 2", dtype=str)

                df_a_clean, warn_a = prepare_file_a(df_a_raw, cfg)
                df_b1, df_b2, warn_b = prepare_file_b(df_b1_raw, df_b2_raw, cfg)

                merged, warn_merge = merge_data(df_a_clean, df_b1, df_b2, cfg)

            with st.spinner("Calculating demand and suggested dispatch..."):
                detail = calculate_demand(merged, cfg, lead_time=lead_time)

            with st.spinner("Generating summary report..."):
                summary = generate_summary(detail, cfg)

            # Display warnings - merge warnings shown prominently if critical
            all_warnings = warn_a + warn_b + warn_merge
            
            # Check for critical Article mismatch
            critical_warnings = [w for w in warn_merge if "CRITICAL" in w or "NO Articles" in w]
            if critical_warnings:
                st.error("🚨 Critical Data Issue Detected:")
                for w in critical_warnings:
                    st.error(w)
                st.warning("⚠️ The calculation will proceed, but promotion targets may not be applied correctly. Please verify your input files.")
            
            if all_warnings:
                with st.expander("Data Quality Warnings", expanded=True if critical_warnings else False):
                    for w in all_warnings:
                        st.warning(w)

            # Main result tabs
            tab1, tab2, tab3 = st.tabs(
                ["Detail Calculation", "Summary Report", "Visualizations"]
            )

            with tab1:
                st.subheader("Detail Calculation")
                st.dataframe(
                    detail[
                        [
                            "Group_No",
                            "Article",
                            "Site",
                            "RP_Type",
                            "Supply_source",
                            "Is_Promo_SKU",
                            "SaSa_Net_Stock",
                            "Pending_Received",
                            "Safety_Stock",
                            "Last_Month_Sold_Qty_capped",
                            "Daily_Sales_Rate",
                            "Effective_Target_Cover_Days",
                            "Base_Demand",
                            "Site_Promo_Demand",
                            "Total_Demand",
                            "Net_Demand_raw",
                            "Net_Demand_for_Dispatch",
                            "MOQ",
                            "Suggested_Dispatch_Qty",
                            "Dispatch_Type",
                        ]
                    ],
                    use_container_width=True,
                )

            with tab2:
                st.subheader("Summary Report (Group No. + SKU)")
                st.dataframe(
                    summary,
                    use_container_width=True,
                )

            with tab3:
                st.subheader("SKU Demand vs. Available Stock (Exclude D001)")
                # Exclude DC site for this chart
                detail_non_dc = detail[detail["Site"] != cfg.DC_SITE_CODE].copy()
                if not detail_non_dc.empty:
                    # Aggregate by Article: only compute Total_Demand here
                    chart_df = (
                        detail_non_dc.groupby("Article", as_index=False)
                        .agg(Total_Demand=("Total_Demand", "sum"))
                    )

                    # Bring in Total_Stock_Available from summary (already aggregated by Article)
                    if "Total_Stock_Available" in summary.columns:
                        sum_stock = (
                            summary[["Article", "Total_Stock_Available"]]
                            .drop_duplicates(subset=["Article"])
                        )
                        chart_df = chart_df.merge(
                            sum_stock,
                            on="Article",
                            how="left",
                        )
                    else:
                        chart_df["Total_Stock_Available"] = 0

                    st.bar_chart(
                        chart_df.set_index("Article")[["Total_Demand", "Total_Stock_Available"]]
                    )
                else:
                    st.info("No non-D001 data available for the chart.")

                st.subheader("Net Demand Heatmap (Exclude D001)")
                if not detail_non_dc.empty:
                    pivot = detail_non_dc.pivot_table(
                        index="Article",
                        columns="Site",
                        values="Net_Demand_for_Dispatch",
                        aggfunc="sum",
                        fill_value=0,
                    )
                    # Use plain table to avoid matplotlib dependency on Streamlit Cloud
                    st.dataframe(pivot)
                else:
                    st.info("No non-D001 data available for heatmap.")

            # Prepare downloadable Excel
            with st.spinner("Preparing Excel export..."):
                output_buffer = io.BytesIO()
                export_to_excel(
                    detail=detail,
                    summary=summary,
                    df_a_clean=df_a_clean,
                    df_b1=df_b1,
                    df_b2=df_b2,
                    output_path=output_buffer,
                )
                output_buffer.seek(0)

            st.download_button(
                label="下載 Excel 報告 / Download Excel Report",
                data=output_buffer,
                file_name="Promotion_Planning_Result.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )

            st.success("分析完成。你可以在上方查看結果、圖表，並下載 Excel 報告。")

        except Exception as e:
            st.error(f"Error during processing: {e}")


if __name__ == "__main__":
    run_app()