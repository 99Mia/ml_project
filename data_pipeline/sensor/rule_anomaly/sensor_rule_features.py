def add_sensor_rule_features(df):
    df = df.copy()

    # 파생 feature
    df["sensor_delta_temp"] = df["process_temp_k"] - df["air_temp_k"]

    return df