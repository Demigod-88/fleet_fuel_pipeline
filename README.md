```markdown
# ⛽ Automated Fleet Fuel Reconciliation & Fraud Detection Pipeline

An enterprise-grade, containerized data engineering pipeline designed to automate the reconciliation of commercial fuel card transactions against real-time vehicle telematics. Built to eliminate manual auditing bottlenecks, detect fuel fraud, and deliver executive-level financial risk visibility.

---

## 🏗️ Architecture & Technology Stack


```

[ Raw Fuel Transactions ] ──┐
├──> [ PostgreSQL Staging & Dims ] ──> [ Airflow 3 Orchestration ] ──> [ Fact Reconciler ] ──> [ Executive Audit Reporting ]
[ Real-time Telematics ]  ──┘              (fleet_db)                   (@daily DAG Engine)           (SQL & Python)            (Pandas / Matplotlib)

```

* **Orchestration:** Apache Airflow 3 (TaskFlow API, `@dag`, `@task`)
* **Storage & Processing:** PostgreSQL (Star Schema, Window Functions, Spatial Haversine Calculations)
* **Containerization:** Docker & Docker Compose
* **Analytics & Reporting:** Python (`pandas`, `seaborn`, `matplotlib`)
* **Data Quality:** Automated SLA assertions and anomaly flagging

---

## 📊 Core Business Rules & Fraud Logic

The reconciliation engine executes a heavy-lifting SQL transformation pipeline evaluating three core anomaly vectors:

1. **Location Mismatch (`flag_location_mismatch`):** Flags transactions where the vehicle's telematics GPS location was $> 1.0\text{ km}$ away from the fueling station during the card swipe timestamp.
2. **Volume Overflow (`flag_volume_overflow`):** Detects single-swipe fuel purchases exceeding the vehicle's physical maximum tank capacity (e.g., pumping 450L into a 350L capacity tank).
3. **Gauge Discrepancy (`flag_fuel_discrepancy`):** Identifies off-tank filling or skimming by comparing purchased card volumes against actual telemetry gauge deltas with a $>15\%$ variance threshold.

---

## 📂 Project Directory Structure

```text
fleet_fuel_pipeline/
│
├── dags/
│   └── fleet_fuel_reconciliation_engine.py  # Airflow 3 DAG definition
├── sql/
│   └── init_fleet_db.sql                    # Star schema & synthetic seed data
├── scripts/
│   └── generate_fleet_report.py             # Executive audit visualization engine
├── docker-compose.yaml                      # Local infrastructure setup
├── fleet_reconciliation_report.png          # Generated executive audit dashboard
└── README.md                                # Project documentation

```

---

## 🚀 Quickstart & Deployment

### 1. Initialize Infrastructure

Spin up the containerized PostgreSQL database and Apache Airflow 3 environment:

```powershell
docker compose up -d

```

### 2. Set Up Database Schema & Seed Data

Execute the initialization SQL script inside the database container to populate dimensions, vehicles, and raw staging streams:

```powershell
docker exec -i postgres psql -U airflow -d fleet_db < sql/init_fleet_db.sql

```

### 3. Trigger the Airflow Pipeline

Sync or copy the DAG into the Airflow container, reserialize the DAG bag, and trigger a test run:

```powershell
docker exec -u airflow -it airflow airflow dags reserialize
docker exec -u airflow -it airflow airflow dags trigger fleet_fuel_reconciliation_engine

```

### 4. Generate the Executive Audit Report

Run the Python reporting script to query the analytical fact table and compile financial exposure metrics:

```powershell
docker cp scripts/generate_fleet_report.py airflow:/opt/airflow/generate_fleet_report.py
docker exec -u airflow -it airflow python /opt/airflow/generate_fleet_report.py
docker cp airflow:/opt/airflow/fleet_reconciliation_report.png .

```

---

## 📈 Executive Audit Findings

Running the reconciliation pipeline against the fleet dataset yields immediate financial risk visibility:

* **Total Fleet Spend:** `$8,160.00`
* **Flagged Risk Exposure:** `$6,960.00` (`85.3%` leakage across 3 of 4 transactions)
* **Primary Loss Vector:** Tank Capacity Overflows account for the highest single financial impact (~`$3,600`), followed closely by Off-Tank Gauge Discrepancies (~`$2,400`) and Geospatial Location Mismatches (~`$960`).

### Executive Audit Dashboard Preview

---

## 💡 Key Engineering Highlights

* **Idempotent Upserts:** Utilizes PostgreSQL `ON CONFLICT (transaction_id) DO UPDATE` to ensure safe, repeatable pipeline reruns without duplicate record creation.
* **Geospatial Processing:** Implements native SQL-based Haversine distance calculations directly in the transformation layer to match latitude/longitude coordinates against fuel station pings.
* **Production-Grade Data Quality:** Built-in Airflow tasks enforce hard SLA checks—halting downstream execution if raw-to-fact row counts mismatch or primary identifiers contain null values.

```

```
