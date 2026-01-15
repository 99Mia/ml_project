# CSV -> DataFrame

import pandas as pd
from data_pipeline.sensor.raw.schema import COLUMNS
from config import DATA_DIR, SENSOR_RAW_CSV

def read_sensor_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = COLUMNS
    return df

"""
DataFrame으로 바꾸는 이유 : 
- 컬럼명 통일
- 전처리 / feature 추가
- DB, AI, 시각화 전부 공통 포맷
"""

def save_sensor_csv(df: pd.DataFrame, csv_path:str):
    df.to_csv(csv_path, index=False) # -> 기존 csv 파일이 있으면 덮어쓰고, 인덱스는 제외
    print(f"CSV 저장 완료: {csv_path}")




