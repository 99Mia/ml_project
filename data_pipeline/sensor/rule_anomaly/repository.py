# DB -> DataFrame -> DB
# DB 연결, 테이블 읽기, 테이블 저장 등 데이터 입출력 담당

import pandas as pd
from config import DB_CONFIG
from config import get_engine


# DB 에서 데이터 가져오기
def read_sensor_raw():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM sensor_raw", engine)


def save_anomalies(df, table_name="sensor_rule_anomaly"):
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"DB 저장 완료: {table_name}")