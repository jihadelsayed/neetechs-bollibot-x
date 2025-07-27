import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from apexomni.http_private_sign import HttpPrivateSign  # ✅ CORRECT CLASS

# Connect to client
client = HttpPrivateSign(
    endpoint="https://api.apex.exchange",
    api_key_credentials={
        "key": "c858b2ac-aecd-0e4d-ea41-1cca664cdc2a",
        "secret": "esdV7zDm0m7xIEcuwB9F6rcEU0bASN15oYL5zk9W",
        "passphrase": "u226nDR0kEoIJfsTLiAy"
    },
    eth_private_key="0xa3c09b7ed2f38a836c9db6c0c03e4efc5f72c1348f2f6b3ae3277e0f50476b55"
)

# Optional sanity check
print(client.get_account())

# Real order
resp = client.create_order_v3(
    symbol="SOLUSDT",
    side="BUY",
    type="MARKET",
    qty=1.0,
    timeInForce="IOC"
)

print("✅ Order Placed:", resp)