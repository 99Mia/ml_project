"""
Rule 기반 이상치 감지 pipeline
1. config/yaml 읽기 -> threshold, 컬럼, feature, output 정보 가져오기
2. db에서 sensor_raw 읽기 -> repository.py 사용
3. 파생 feature 추가 -> sensor_rule_features.py 사용
4. Threshold 계산 + 이상치 감지 -> rule_logic.py 사용
5. db에 결과 저장 -> repository.py 사용
6. 로그/콘솔 출력
"""


import logging
from repository import read_sensor_raw, save_anomalies
from sensor_rule_features import add_sensor_rule_features
from rule_logic import calculate_stat_thresholds, calculate_iqr_thresholds, detect_anomalies
from config import RULE_CONFIG



# congfig 에서 설정 가져오기
columns = RULE_CONFIG.get("columns") # 분석 대상 컬럼, 없으면 None -> 자동선택
threshold_config = RULE_CONFIG.get("threshold",{})
features_config = RULE_CONFIG.get("features", {})
output_config = RULE_CONFIG.get("output", {})
save_columns = output_config.get("save_columns") # db에 저장할 컬럼 리스트

# db에서 sensor_raw 읽기
df = read_sensor_raw()

# 파생 feature 추가
df = add_sensor_rule_features(
  df,
  use_delta_temp=features_config.get("use_delta_temp",True)
  )

# threshold 계산
if threshold_config.get("method") == "iqr":
  thresholds = calculate_iqr_thresholds(df, columns)
else: # 기본 stat 방식
  thresholds = calculate_stat_thresholds(df, columns)

# 이상치 감지
df = detect_anomalies(
  df,
  thresholds,
  prefix="rule",
  save_cols=save_columns
)

# db에 결과 저장
tabel_name = output_config.get("table_name", "sensor_rule_anomaly")
save_anomalies(df, table_name=tabel_name)

# 콘솔/로그 출력
print(f"Rule 기반 이상치 감지 완료. DB 저장 : {tabel_name}")
logging.info(f"Rule 기반 이상치 감지 완료. DB 저장 : {tabel_name}")





