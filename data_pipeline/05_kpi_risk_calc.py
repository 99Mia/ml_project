# 05_kpi_risk_calc.py
import pandas as pd
import numpy as np
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="psh",
    password="1234",
    database="ml_db"
)
cursor = conn.cursor()

plc_df = pd.read_sql("SELECT * FROM plc_log", conn)

# EWMA
plc_df['torque_ewma'] = plc_df['torque_nm'].ewm(span=10).mean()
plc_df['rpm_ewma'] = plc_df['rotational_speed_rpm'].ewm(span=10).mean()

# 동적 Threshold
torque_std = plc_df['torque_nm'].rolling(window=10).std()
plc_df['risk_level'] = np.where(
    (plc_df['torque_ewma'] > plc_df['torque_ewma'].mean()+2*torque_std) |
    (plc_df['torque_ewma'] < plc_df['torque_ewma'].mean()-2*torque_std),
    'High','Normal'
)

# KPI 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS kpi (
    udi INT PRIMARY KEY,
    timestamp DATETIME,
    risk_level VARCHAR(10),
    torque_ewma FLOAT,
    rpm_ewma FLOAT
);
""")
conn.commit()

insert_sql = """
INSERT INTO kpi (udi, timestamp, risk_level, torque_ewma, rpm_ewma)
VALUES (%s,%s,%s,%s,%s)
"""
cursor.executemany(insert_sql, plc_df[['udi','timestamp','risk_level','torque_ewma','rpm_ewma']].values.tolist())
conn.commit()
print("KPI / Risk Level 데이터 삽입 완료")
conn.close()