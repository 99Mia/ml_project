import os
from sqlalchemy import create_engine
import  yaml

# 프로젝트 루트 기준 계산

# 현재 파일 위치
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# 데이터 경로 설정
DATA_DIR = os.path.join(PROJECT_ROOT, "data") 
SENSOR_RAW_CSV = os.path.join(DATA_DIR, "sensor_raw.csv")
SENSOR_RAW_CLEAN_CSV = os.path.join(DATA_DIR, "sensor_raw_clean.csv")


# DB 접속 성보
DB_CONFIG = {
  "host": "127.0.0.1",
  "port": 3306,
  "user": "psh",
  "password": "1234",
  "database": "ml_db"
}

# SQLALchemy Engine 생성 함수
def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


PIPELINE_OPTIONS = {
  "chunk_size": 5000,
  "log_level": "INFO"
}

# Rule YAMY 파일 읽기
RULE_YAML_PATH = os.path.join(PROJECT_ROOT, "data_pipeline", "sensor", "rule_anomaly", "config", "rule_anomaly.yaml")
with open(RULE_YAML_PATH, "r") as f:
  RULE_CONFIG = yaml.safe_load(f)