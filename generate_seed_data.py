# generate_seed_data.py
import psycopg2
from datetime import datetime, timedelta

CONN_STR = "host=postgres dbname=fleet_db user=airflow password=airflow port=5432"

def seed_database():
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()

    # 1. Seed Dimensions
    cur.execute("""
        INSERT INTO dim_vehicle (vehicle_id, license_plate, make_model, max_tank_capacity_l, primary_depot)
        VALUES 
            ('VEH-001', 'GT-102-24', 'Volvo FH16', 400.00, 'Accra Central Depot'),
            ('VEH-002', 'GT-505-25', 'Scania R500', 350.00, 'Tema Logistics Hub'),
            ('VEH-003', 'GT-909-26', 'MAN TGX', 450.00, 'Takoradi Port Terminal')
        ON CONFLICT DO NOTHING;

        INSERT INTO dim_fuel_card (card_number, vehicle_id, driver_name)
        VALUES 
            ('CARD-8801', 'VEH-001', 'Kwame Mensah'),
            ('CARD-8802', 'VEH-002', 'Kofi Addo'),
            ('CARD-8803', 'VEH-003', 'Yaw Osei')
        ON CONFLICT DO NOTHING;
    """)

    base_time = datetime(2026, 9, 2, 8, 0, 0)

    # 2. Seed Clean Match (VEH-001)
    cur.execute("""
        INSERT INTO raw_fuel_transactions VALUES 
        ('TXN-1001', 'CARD-8801', %s, 'STATION-ACCRA-01', 5.6037, -0.1870, 150.00, 1200.00)
        ON CONFLICT DO NOTHING;
    """, (base_time,))
    cur.execute("""
        INSERT INTO raw_telematics_logs (vehicle_id, ping_time, gps_lat, gps_long, fuel_level_pct, odometer_km)
        VALUES 
            ('VEH-001', %s, 5.6038, -0.1871, 20.00, 125000.00),
            ('VEH-001', %s, 5.6037, -0.1870, 57.50, 125000.00);
    """, (base_time - timedelta(minutes=5), base_time + timedelta(minutes=5)))

    # 3. FRAUD 1: Location Mismatch (VEH-002, GPS is 15 km away during swipe)
    t2 = base_time + timedelta(hours=2)
    cur.execute("""
        INSERT INTO raw_fuel_transactions VALUES 
        ('TXN-1002', 'CARD-8802', %s, 'STATION-TEMA-05', 5.6351, -0.0166, 120.00, 960.00)
        ON CONFLICT DO NOTHING;
    """, (t2,))
    cur.execute("""
        INSERT INTO raw_telematics_logs (vehicle_id, ping_time, gps_lat, gps_long, fuel_level_pct, odometer_km)
        VALUES ('VEH-002', %s, 5.7500, -0.1500, 30.00, 89000.00);
    """, (t2,))

    # 4. FRAUD 2: Volume Overflow (VEH-002, 450L charged on a 350L max tank)
    t3 = base_time + timedelta(hours=4)
    cur.execute("""
        INSERT INTO raw_fuel_transactions VALUES 
        ('TXN-1003', 'CARD-8802', %s, 'STATION-TEMA-02', 5.6350, -0.0165, 450.00, 3600.00)
        ON CONFLICT DO NOTHING;
    """, (t3,))
    cur.execute("""
        INSERT INTO raw_telematics_logs (vehicle_id, ping_time, gps_lat, gps_long, fuel_level_pct, odometer_km)
        VALUES ('VEH-002', %s, 5.6351, -0.0166, 10.00, 89200.00);
    """, (t3,))

    # 5. FRAUD 3: Off-Tank Filling / Gauge Discrepancy (VEH-003, 300L charged, gauge only rises by 20L)
    t4 = base_time + timedelta(hours=6)
    cur.execute("""
        INSERT INTO raw_fuel_transactions VALUES 
        ('TXN-1004', 'CARD-8803', %s, 'STATION-TAKORADI-01', 4.8980, -1.7550, 300.00, 2400.00)
        ON CONFLICT DO NOTHING;
    """, (t4,))
    cur.execute("""
        INSERT INTO raw_telematics_logs (vehicle_id, ping_time, gps_lat, gps_long, fuel_level_pct, odometer_km)
        VALUES 
            ('VEH-003', %s, 4.8981, -1.7551, 10.00, 45000.00),
            ('VEH-003', %s, 4.8981, -1.7551, 14.44, 45000.00);
    """, (t4 - timedelta(minutes=3), t4 + timedelta(minutes=5)))

    conn.commit()
    cur.close()
    conn.close()
    print("[Seed Engine] Enterprise seed dataset initialized cleanly!")

if __name__ == '__main__':
    seed_database()