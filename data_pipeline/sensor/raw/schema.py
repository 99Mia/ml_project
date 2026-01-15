# 컬럼명 / 타입 정의

# sensor/raw/schema.py

TABLE_NAME = "sensor_raw"

COLUMNS = [
    "sensor_prod_udi",          # 제품 식별자
    "sensor_prod_id",           # 제품 ID
    "sensor_prod_type",         # 제품 타입

    "sensor_air_temp_k",        # 공기 온도
    "sensor_process_temp_k",    # 공정 온도
    "sensor_rot_speed_rpm",     # 회전 속도
    "sensor_torque_nm",         # 토크
    "sensor_tool_wear_min",     # 공구 마모

    "sensor_flag_machine_failure",  # 설비 고장 여부
    "sensor_flag_twf",              # tool wear failure
    "sensor_flag_hdf",              # heat dissipation failure
    "sensor_flag_pwf",              # power failure
    "sensor_flag_osf",              # other sensor failure
    "sensor_flag_rnf"               # random failure
]


# CREATE TABLE SQL
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    sensor_prod_udi INT PRIMARY KEY,
    sensor_prod_id VARCHAR(20),
    sensor_prod_type CHAR(1),

    sensor_air_temp_k FLOAT,
    sensor_process_temp_k FLOAT,
    sensor_rot_speed_rpm INT,
    sensor_torque_nm FLOAT,
    sensor_tool_wear_min INT,

    sensor_flag_machine_failure TINYINT,
    sensor_flag_twf TINYINT,
    sensor_flag_hdf TINYINT,
    sensor_flag_pwf TINYINT,
    sensor_flag_osf TINYINT,
    sensor_flag_rnf TINYINT
);
"""