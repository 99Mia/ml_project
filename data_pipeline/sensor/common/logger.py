import logging

def get_logger(name="sensor"):
    logging.basicConfig(
        filename="anomaly_log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(name)