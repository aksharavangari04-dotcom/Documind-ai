import requests
from config import BASE_URL


def login(phone, password):

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "phone": phone,
            "password": password
        }
    )

    return response
