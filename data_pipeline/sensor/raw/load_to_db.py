# INSERT
# DataFrame -> MySQL


def load_dataframe_to_db(df, conn, table_name: str):
    cursor = conn.cursor()

    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    insert_sql = f"""
    INSERT INTO {table_name} ({columns})
    VALUES ({placeholders})
    """

    cursor.executemany(insert_sql, df.values.tolist())
    conn.commit()