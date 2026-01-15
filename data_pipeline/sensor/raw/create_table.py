# sensor/raw/create_table.py


from data_pipeline.sensor.raw.schema import CREATE_TABLE_SQL

def create_sensor_raw_table(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS sensor_raw")
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print("sensor_raw 테이블 생성 완료") 