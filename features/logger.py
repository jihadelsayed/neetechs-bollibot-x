import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_trade(message):
    logging.info(message)
    with open("trades.log", "a") as f:
        f.write(f"{datetime.now()} - {message}\n")