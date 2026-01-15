# 02_quality_simulation_realistic_v2.py
import pandas as pd
import numpy as np
import mysql.connector

# ------------------------------
# 1. DB 연결
# ------------------------------
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="psh",
    password="1234",
    database="ml_db"
)
cursor = conn.cursor()

# ------------------------------
# 2. sensor_raw 불러오기
# ------------------------------
sensor_df = pd.read_sql("SELECT * FROM sensor_raw", conn)

# ------------------------------
# 2-1. 장비 ID 추가 (실제 PLC 로그 기반 시뮬레이션)
# ------------------------------
np.random.seed(42)
equipment_ids = ['EQ1','EQ2','EQ3','EQ4']
sensor_df['equipment_id'] = np.random.choice(equipment_ids, size=len(sensor_df))

# ------------------------------
# 3. Quality 시뮬레이션 + KPI / Residual / Risk Level
# ------------------------------
quality_df = sensor_df[['udi','product_id','product_type','tool_wear_min','torque_nm','air_temp_k','equipment_id']].copy()

# EWMA + Rolling std 기반 동적 Defect 판단
span = 20
window = 20

# 그룹화: 장비 + 제품 타입 기준 이
group_cols = ['equipment_id','product_type']

for col in ['tool_wear_min','torque_nm']:
    ewma_col = f"{col}_ewma"
    std_col = f"{col}_std"
    quality_df[ewma_col] = quality_df.groupby(group_cols)[col].transform(lambda x: x.ewm(span=span).mean())
    quality_df[std_col] = quality_df.groupby(group_cols)[col].transform(lambda x: x.rolling(window).std())

# ΔT 계산: 장비 기준 시계열
quality_df['delta_temp'] = quality_df.groupby('equipment_id')['air_temp_k'].transform(lambda x: x - x.rolling(window).mean())

# 동적 Threshold 적용: Defect Flag
quality_df['defect_flag'] = (
    (quality_df['tool_wear_min'] > quality_df['tool_wear_min_ewma'] + 2*quality_df['tool_wear_min_std']) |
    (quality_df['torque_nm'] > quality_df['torque_nm_ewma'] + 2*quality_df['torque_nm_std']) |
    (quality_df['delta_temp'] > 2)
).astype(int)

# 공정 단계 / tool 교체 여부 시뮬레이션
process_steps = ['A','B','C']
quality_df['process_step'] = np.random.choice(process_steps, len(quality_df))
quality_df['tool_replaced'] = np.random.choice([0,1], len(quality_df))

# Spec1 / Spec2 계산 (현장 기준 오차 수준 최소화)
def calc_spec1(row):
    base = 10 if row['product_type']=='M' else 12
    if row['process_step']=='B':
        base += 0.5
    if row['tool_replaced']==1:
        base += 0.3
    return base + np.random.normal(0,0.05)

def calc_spec2(row):
    base = 20 if row['product_type']=='M' else 18
    if row['process_step']=='C':
        base -= 0.3
    if row['tool_replaced']==1:
        base += 0.2
    return base + np.random.normal(0,0.05)

quality_df['spec1'] = quality_df.apply(calc_spec1, axis=1)
quality_df['spec2'] = quality_df.apply(calc_spec2, axis=1)

# ------------------------------
# 3-1. Residual 계산: RPM-Torque 관계
# ------------------------------
# 단일 기준선 (정상 Torque ≈ f(RPM))
from sklearn.linear_model import LinearRegression

residuals = []
for eq in equipment_ids:
    for pt in quality_df['product_type'].unique():
        mask = (quality_df['equipment_id']==eq) & (quality_df['product_type']==pt)
        X = quality_df.loc[mask, ['rotational_speed_rpm']].values
        y = quality_df.loc[mask, 'torque_nm'].values
        if len(X) > 1:
            model = LinearRegression().fit(X, y)
            pred = model.predict(X)
            quality_df.loc[mask, 'torque_pred'] = pred
            quality_df.loc[mask, 'residual'] = y - pred
        else:
            quality_df.loc[mask, 'torque_pred'] = y
            quality_df.loc[mask, 'residual'] = 0

# ------------------------------
# 3-2. Risk Level 계산 (Residual 기반)
# ------------------------------
# Residual 이상치: EWMA + 2*rolling std
quality_df['residual_ewma'] = quality_df.groupby(group_cols)['residual'].transform(lambda x: x.ewm(span=span).mean())
quality_df['residual_std'] = quality_df.groupby(group_cols)['residual'].transform(lambda x: x.rolling(window).std())

quality_df['risk_level'] = np.where(
    (quality_df['residual'] > quality_df['residual_ewma'] + 2*quality_df['residual_std']) |
    (quality_df['residual'] < quality_df['residual_ewma'] - 2*quality_df['residual_std']),
    'High','Normal'
)

# ------------------------------
# 4. DB 테이블 생성 (Quality + KPI 포함)
# ------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS quality_kpi (
    udi INT PRIMARY KEY,
    product_id VARCHAR(20),
    product_type CHAR(1),
    equipment_id VARCHAR(10),
    process_step CHAR(1),
    tool_replaced TINYINT,
    tool_wear_min FLOAT,
    torque_nm FLOAT,
    defect_flag TINYINT,
    spec1 FLOAT,
    spec2 FLOAT,
    tool_wear_min_ewma FLOAT,
    tool_wear_min_std FLOAT,
    torque_nm_ewma FLOAT,
    torque_nm_std FLOAT,
    delta_temp FLOAT,
    torque_pred FLOAT,
    residual FLOAT,
    residual_ewma FLOAT,
    residual_std FLOAT,
    risk_level VARCHAR(10)
);
""")
conn.commit()

# ------------------------------
# 5. DB 삽입
# ------------------------------
insert_cols = [
    'udi','product_id','product_type','equipment_id','process_step','tool_replaced',
    'tool_wear_min','torque_nm','defect_flag','spec1','spec2',
    'tool_wear_min_ewma','tool_wear_min_std','torque_nm_ewma','torque_nm_std','delta_temp',
    'torque_pred','residual','residual_ewma','residual_std','risk_level'
]
insert_sql = f"INSERT INTO quality_kpi ({','.join(insert_cols)}) VALUES ({','.join(['%s']*len(insert_cols))})"
cursor.executemany(insert_sql, quality_df[insert_cols].values.tolist())
conn.commit()

print("Quality + KPI 데이터 삽입 완료")
conn.close()

