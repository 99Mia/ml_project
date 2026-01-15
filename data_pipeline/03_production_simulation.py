# 02_quality_simulation_real.py
import pandas as pd
import numpy as np
import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="psh",
    password="1234",
    database="ml_db"
)
cursor = conn.cursor()

# sensor_raw 불러오기
sensor_df = pd.read_sql("SELECT * FROM sensor_raw", conn)

# -----------------------------
# Feature / KPI 생성
# -----------------------------

# EWMA, rolling std
sensor_df['torque_ewma'] = sensor_df['torque_nm'].ewm(span=10).mean()
sensor_df['torque_std'] = sensor_df['torque_nm'].rolling(window=10).std()
sensor_df['rpm_ewma'] = sensor_df['rotational_speed_rpm'].ewm(span=10).mean()

# RPM-Torque 기준선 잔차
rpm_mean = sensor_df.groupby('rotational_speed_rpm')['torque_nm'].transform('mean')
sensor_df['residual'] = sensor_df['torque_nm'] - rpm_mean

# Anomaly Score
sensor_df['anomaly_score'] = np.abs(sensor_df['residual']) / (sensor_df['residual'].rolling(10).std() + 1e-6)

# Risk Level
sensor_df['risk_level'] = np.where(sensor_df['anomaly_score'] > 2, 'High', 'Normal')

# Defect Flag (EWMA + 조건 기반)
def calc_defect(row):
    torque_thresh = row['torque_ewma'] + 2*row['torque_std']  # 동적 Threshold
    if row['tool_wear_min'] > 200 or row['torque_nm'] > torque_thresh:
        return 1
    return 0
sensor_df['defect_flag'] = sensor_df.apply(calc_defect, axis=1)

# Spec 값: 공정 조건 기반 + 최소 노이즈
sensor_df['spec1'] = np.where(sensor_df['product_type']=='M', 10+np.random.normal(0,0.05,len(sensor_df)), 12+np.random.normal(0,0.05,len(sensor_df)))
sensor_df['spec2'] = np.where(sensor_df['product_type']=='M', 20+np.random.normal(0,0.1,len(sensor_df)), 18+np.random.normal(0,0.1,len(sensor_df)))

# KPI 포함 DataFrame
quality_df = sensor_df[['udi','product_id','defect_flag','spec1','spec2','torque_ewma','rpm_ewma','residual','anomaly_score','risk_level']]

# -----------------------------
# DB 삽입
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS quality (
    udi INT PRIMARY KEY,
    product_id VARCHAR(20),
    defect_flag TINYINT,
    spec1 FLOAT,
    spec2 FLOAT,
    torque_ewma FLOAT,
    rpm_ewma FLOAT,
    residual FLOAT,
    anomaly_score FLOAT,
    risk_level VARCHAR(10)
);
""")
conn.commit()

insert_sql = """
INSERT INTO quality (udi, product_id, defect_flag, spec1, spec2, torque_ewma, rpm_ewma, residual, anomaly_score, risk_level)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""
cursor.executemany(insert_sql, quality_df.values.tolist())
conn.commit()
print("현장 수준 Quality + KPI 데이터 삽입 완료")
conn.close()