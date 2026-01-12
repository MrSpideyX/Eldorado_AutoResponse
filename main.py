import os
import time
import json
import requests
from pycognito import AWSSRP
import boto3

# ENV VARIABLES
EMAIL = os.getenv("ELDORADO_EMAIL")
PASSWORD = os.getenv("ELDORADO_PASSWORD")
POOL_ID = os.getenv("COGNITO_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
HOSTNAME = os.getenv("ELDORADO_HOSTNAME")

ORDERS_FILE = "orders.json"

cognito = boto3.client("cognito-idp", region_name="us-east-2")

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f)

# STEP 1 — LOGIN & GET ID TOKEN
def get_id_token():
    aws = AWSSRP(
        username=EMAIL,
        password=PASSWORD,
        pool_id=POOL_ID,
        client_id=CLIENT_ID,
        client=cognito
    )

    auth_params = aws.get_auth_params()
    response = cognito.initiate_auth(
        AuthFlow="USER_SRP_AUTH",
        AuthParameters=auth_params,
        ClientId=CLIENT_ID
    )

    challenge = aws.process_challenge(
        response["ChallengeParameters"],
        auth_params
    )

    final = cognito.respond_to_auth_challenge(
        ClientId=CLIENT_ID,
        ChallengeName="PASSWORD_VERIFIER",
        ChallengeResponses=challenge
    )

    return final["AuthenticationResult"]["IdToken"]

# STEP 2 — GET MY ORDERS
def get_my_orders(id_token):
    headers = {
        "Accept": "application/json",
        "Cookie": f"__Host-EldoradoIdToken={id_token}"
    }

    r = requests.get(
        f"https://{HOSTNAME}/api/orders/me",
        headers=headers
    )

    if r.status_code == 200:
        return r.json()
    return []

def main():
    processed = load_orders()

    while True:
        try:
            id_token = get_id_token()
            orders = get_my_orders(id_token)

            for order in orders:
                order_id = order["id"]

                if order_id not in processed:
                    print(f"🆕 New order detected: {order_id}")
                    # FUTURE: auto message endpoint here
                    processed.append(order_id)
                    save_orders(processed)

        except Exception as e:
            print("Error:", e)

        time.sleep(60)

if __name__ == "__main__":
    main()
