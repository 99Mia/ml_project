from sqlalchemy import create_engine

def get_engine():
    return create_engine(
        "mysql+mysqlconnector://psh:1234@127.0.0.1:3306/ml_db"
    )