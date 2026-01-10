import time
import json
import requests

ORDERS_FILE = "orders.json"

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(order_ids):
    with open(ORDERS_FILE, "w") as f:
        json.dump(order_ids, f)

def check_new_orders():
    # Will be filled after Eldorado API access
    return []

def send_auto_message(order_id):
    # Will be filled after Eldorado API access
    print(f"Auto reply sent for order {order_id}")

def main():
    processed_orders = load_orders()

    while True:
        new_orders = check_new_orders()

        for order in new_orders:
            if order not in processed_orders:
                send_auto_message(order)
                processed_orders.append(order)
                save_orders(processed_orders)

        time.sleep(60)

if __name__ == "__main__":
    main()
