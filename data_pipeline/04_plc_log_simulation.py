# 04_plc_log_simulation.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="psh",
    password="1234",
    database="ml_db"
)
cursor = conn.cursor()

sensor_df = pd.read_sql("SELECT * FROM sensor_raw", conn)
timestamps = [datetime(2026,1,13,8,0,0) + timedelta(minutes=i) for i in range(len(sensor_df))]

plc_df = pd.DataFrame({
    'udi': sensor_df['udi'],
    'timestamp': timestamps,
    'rotational_speed_rpm': sensor_df['rotational_speed_rpm'],
    'torque_nm': sensor_df['torque_nm'],
    'air_temp_k': sensor_df['air_temp_k'],
    'process_temp_k': sensor_df['process_temp_k'],
})

cursor.execute("""
CREATE TABLE IF NOT EXISTS plc_log (
    udi INT PRIMARY KEY,
    timestamp DATETIME,
    rotational_speed_rpm INT,
    torque_nm FLOAT,
    air_temp_k FLOAT,
    process_temp_k FLOAT
);
""")
conn.commit()

insert_sql = """
INSERT INTO plc_log (udi, timestamp, rotational_speed_rpm, torque_nm, air_temp_k, process_temp_k)
VALUES (%s,%s,%s,%s,%s,%s)
"""
cursor.executemany(insert_sql, plc_df.values.tolist())
conn.commit()
print("PLC Log 데이터 삽입 완료")
conn.close()