# sensor_anomaly_batch.py
import pandas as pd
import numpy as np
import mysql.connector
from sqlalchemy import create_engine
import logging

# -----------------------------
# 1. 로그 설정
# -----------------------------
logging.basicConfig(
    filename="anomaly_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# 2. DB 연결
# -----------------------------
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="psh",
    password="1234",
    database="ml_db"
)
cursor = conn.cursor()

engine = create_engine("mysql+mysqlconnector://psh:1234@127.0.0.1:3306/ml_db")

# -----------------------------
# 3. 데이터 읽어오기
# -----------------------------
df = pd.read_sql("SELECT * FROM sensor_raw", engine)

df["sensor_delta_temp"] = df["process_temp_k"] - df["air_temp_k"]

# -----------------------------
# 4. 분석할 컬럼 정의
# -----------------------------
cols = ["air_temp_k", "process_temp_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min"]
cols.append("sensor_delta_temp")
# -----------------------------
# 5. Threshold 계산 함수
# -----------------------------
def calculate_stat_thresholds(df, cols):
    return {col: (df[col].mean() - 3*df[col].std(),
                  df[col].mean() + 3*df[col].std()) for col in cols}

def calculate_iqr_thresholds(df, cols):
    thresholds = {}
    for col in cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        thresholds[col] = (q1 - 1.5*iqr, q3 + 1.5*iqr)
    return thresholds

# -----------------------------
# 6. 컬럼별 이상치 계산 + row 단위 OR
# -----------------------------
def detect_anomalies(df, thresholds, prefix):
    df_flags = pd.DataFrame(index=df.index)
    row_flags = pd.Series(0, index=df.index)

    for col, (low, high) in thresholds.items():
        anomaly_col = f"{col}_{prefix}_anomaly"
        df_flags[anomaly_col] = (df[col] < low) | (df[col] > high)
        row_flags |= df_flags[anomaly_col]

        # 안전하게 원본 df 값 가져오기
        anomalies_idx = df_flags.index[df_flags[anomaly_col]]
        anomalies = df.loc[anomalies_idx, [col]]

        # 로그/콘솔 출력
        logging.info(f"{col} {prefix} 이상치 수: {len(anomalies)}")
        if len(anomalies) > 0:
            logging.info(anomalies.head().to_string())
            print(f"{col} {prefix} 이상치 수: {len(anomalies)}")
            print(anomalies.head())

    # 전체 row 단위 이상치 컬럼 추가
    # 즉, 다섯개 센서 컬럼 중 하나라도 이상치이면, 그 행 전체를 True로 표시
    df_flags[f"{prefix}_anomaly"] = row_flags
    return df_flags



# -----------------------------
# 7. Threshold 계산
# -----------------------------
stat_thresholds = calculate_stat_thresholds(df, cols)
iqr_thresholds = calculate_iqr_thresholds(df, cols)

# -----------------------------
# 8. 이상치 감지
# -----------------------------
df_stat_flags = detect_anomalies(df, stat_thresholds, "rule")
df_iqr_flags = detect_anomalies(df, iqr_thresholds, "iqr")

# -----------------------------
# 9. 결과 통합
# -----------------------------
df = pd.concat([df, df_stat_flags, df_iqr_flags], axis=1)

# -----------------------------
# 10. DB 저장
# -----------------------------
df.to_sql('sensor_anomaly', engine, if_exists='replace', index=False)

print("DB 저장 완료: sensor_anomaly 테이블")
logging.info("DB 저장 완료: sensor_anomaly 테이블")

# 컬럼별 이상치 개수 확인
print("=== Rule 이상치 ===")
for col in cols:
    anomaly_col = f"{col}_rule_anomaly"
    count = df[anomaly_col].sum()
    print(f"{col} Rule 이상치 수: {count}")

print("\n=== IQR 이상치 ===")
for col in cols:
    anomaly_col = f"{col}_iqr_anomaly"
    count = df[anomaly_col].sum()
    print(f"{col} IQR 이상치 수: {count}")

print("=== Stat 기준 Threshold ===")
for col, (low, high) in stat_thresholds.items():
    print(f"{col}: 하한={low:.2f}, 상한={high:.2f}")

print("\n=== IQR 기준 Threshold ===")
for col, (low, high) in iqr_thresholds.items():
    print(f"{col}: 하한={low:.2f}, 상한={high:.2f}")