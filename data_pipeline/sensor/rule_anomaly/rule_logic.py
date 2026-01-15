# threshold 계산, 이상치 감지
import logging

def calculate_stat_thresholds(df, cols):
    return {
        col: (df[col].mean() - 3*df[col].std(),
              df[col].mean() + 3*df[col].std())
        for col in cols
    }

def calculate_iqr_thresholds(df, cols):
    thresholds = {}
    for col in cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        thresholds[col] = (q1 - 1.5*iqr, q3 + 1.5*iqr)
    return thresholds




def detect_anomalies(df, thresholds, prefix, save_cols=None):
    """
    현업용 이상치 탐지 함수
    df: 분석할 데이터프레임
    thresholds: {컬럼명: (low, high)} 형태
    prefix: 접두사 (ex: 'rule', 'iqr')
    save_cols: DB에 저장할 컬럼 리스트. None이면 row_flag만 저장
    """
    df_flags = {}
    row_flags = None

    for col, (low, high) in thresholds.items():
        # 이상치 플래그 계산
        flag = (df[col] < low) | (df[col] > high)
        df_flags[f"{col}_{prefix}_anomaly"] = flag

        # row 단위 이상치
        row_flags = flag if row_flags is None else (row_flags | flag)

        # 로그 출력 (저장 여부와 무관하게 출력)
        anomalies_idx = df.index[flag]
        anomalies = df.loc[anomalies_idx, [col]]
        logging.info(f"{col} {prefix} 이상치 수: {len(anomalies)}")
        if len(anomalies) > 0:
            logging.info(anomalies.head().to_string())
            print(f"{col} {prefix} 이상치 수: {len(anomalies)}")
            print(anomalies.head())

    # row 단위 이상치 컬럼 생성
    df_flags[f"{prefix}_anomaly"] = row_flags

    # DB에 저장할 컬럼만 선택
    if save_cols:
        save_flags = {f"{col}_{prefix}_anomaly": df_flags[f"{col}_{prefix}_anomaly"] 
                      for col in save_cols if f"{col}_{prefix}_anomaly" in df_flags}
        save_flags[f"{prefix}_anomaly"] = row_flags
        return df.assign(**save_flags)

    return df.assign(**df_flags)