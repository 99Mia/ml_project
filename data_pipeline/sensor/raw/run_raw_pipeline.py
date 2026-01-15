# 실행 파일

import mysql.connector

from data_pipeline.sensor.raw.create_table import create_sensor_raw_table
from data_pipeline.sensor.raw.ingest_csv import read_sensor_csv
from data_pipeline.sensor.raw.load_to_db import load_dataframe_to_db
from data_pipeline.sensor.raw.schema import TABLE_NAME
from config import DB_CONFIG, SENSOR_RAW_CSV, SENSOR_RAW_CLEAN_CSV
from data_pipeline.sensor.raw.ingest_csv import save_sensor_csv



# DB 연결

conn = mysql.connector.connect(
     host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    database=DB_CONFIG["database"]
)
print("MySQL 연결 성공")



# 테이블 생성
create_sensor_raw_table(conn)

# CSV 읽기
df = read_sensor_csv(SENSOR_RAW_CSV)
print(df.head())

# CSV 만들기
save_sensor_csv(df, SENSOR_RAW_CLEAN_CSV)

# 데이터 DB에 적재
load_dataframe_to_db(df, conn, TABLE_NAME)

# 연결 종료
conn.close()
print("Pipeline 실행 완료")
