# generate_fleet_report.py
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CONN_STR = "host=postgres dbname=fleet_db user=airflow password=airflow port=5432"

def generate_executive_report():
    conn = psycopg2.connect(CONN_STR)
    query = """
        SELECT 
            f.transaction_id,
            f.vehicle_id,
            v.make_model,
            v.primary_depot,
            t.total_cost,
            f.volume_purchased_l,
            f.distance_station_to_vehicle_km,
            CASE WHEN f.flag_location_mismatch THEN 'Location Mismatch (>1km)'
                 WHEN f.flag_volume_overflow THEN 'Tank Capacity Overflow'
                 WHEN f.flag_fuel_discrepancy THEN 'Off-Tank / Gauge Discrepancy'
                 ELSE 'Normal' END AS anomaly_type,
            (f.flag_location_mismatch OR f.flag_volume_overflow OR f.flag_fuel_discrepancy) AS is_flagged
        FROM fact_fuel_reconciliation f
        JOIN dim_vehicle v ON f.vehicle_id = v.vehicle_id
        JOIN raw_fuel_transactions t ON f.transaction_id = t.transaction_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 3])

    # Panel 0: Executive KPI Banner (Top spanning)
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis('off')
    
    total_spend = df['total_cost'].sum()
    flagged_df = df[df['is_flagged'] == True]
    flagged_spend = flagged_df['total_cost'].sum()
    fraud_pct = (flagged_spend / total_spend) * 100 if total_spend > 0 else 0

    kpi_text = (
        f"EXECUTIVE AUDIT SUMMARY\n"
        f"• Total Fleet Fuel Spend: ${total_spend:,.2f}  |  "
        f"• Flagged Anomaly Spend: ${flagged_spend:,.2f} ({fraud_pct:.1f}% Risk Exposure)\n"
        f"• Total Flagged Incidents: {len(flagged_df)} out of {len(df)} Transactions"
    )
    ax_kpi.text(0.01, 0.5, kpi_text, fontsize=13, fontweight='bold', family='monospace',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='#ffe6e6', edgecolor='#cc0000', linewidth=1.5),
                verticalalignment='center')

    # Panel 1: Fraud Cost Breakdown by Category
    ax_bar = fig.add_subplot(gs[1, 0])
    if not flagged_df.empty:
        cost_by_anomaly = flagged_df.groupby('anomaly_type')['total_cost'].sum().reset_index()
        sns.barplot(data=cost_by_anomaly, x='total_cost', y='anomaly_type', palette='Reds_r', ax=ax_bar)
        ax_bar.set_title('Financial Exposure by Fraud Category ($)', fontsize=11, fontweight='bold')
        ax_bar.set_xlabel('Total Cost Impact', fontsize=9)
        ax_bar.set_ylabel('')
    else:
        ax_bar.text(0.5, 0.5, 'No Anomalies Flagged', ha='center', va='center')

    # Panel 2: Vehicle Risk Profile Scatter
    ax_scatter = fig.add_subplot(gs[1, 1])
    sns.scatterplot(
        data=df, 
        x='distance_station_to_vehicle_km', 
        y='volume_purchased_l', 
        hue='vehicle_id', 
        style='is_flagged',
        s=200, 
        palette='tab10',
        ax=ax_scatter
    )
    ax_scatter.set_title('Volume vs. Telematics Distance (Risk Map)', fontsize=11, fontweight='bold')
    ax_scatter.set_xlabel('Distance from Vehicle Telematics (km)', fontsize=9)
    ax_scatter.set_ylabel('Volume Purchased (Liters)', fontsize=9)

    plt.suptitle('Fleet Fuel Reconciliation & Executive Fraud Audit Report', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    plt.savefig('fleet_reconciliation_report.png', dpi=300, bbox_inches='tight')
    print("[Report Engine] Executive dashboard generated successfully!")

if __name__ == '__main__':
    generate_executive_report()