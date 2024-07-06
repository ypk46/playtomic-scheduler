# Native imports
from datetime import datetime
from typing import Text, Dict, List
from typing_extensions import TypedDict

# 3rd party imports
import pytz
import requests


# Constants
API_URL = "https://playtomic.io/api/v1"
AUTH_URL = "https://playtomic.io/api/v3"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
)


class AuthPayload(TypedDict):
    access_token: Text
    access_token_expiration: Text
    refresh_token: Text
    refresh_token_expriation: Text
    user_id: Text


class PaymentIntent(TypedDict):
    payment_intent_id: Text
    available_payment_methods: List


class Playtomic:

    # Attributes
    email: Text
    password: Text
    session: requests.Session
    access_token: Text
    user_id: Text

    def __init__(self, email: Text, password: Text):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.headers.update(self.__get_headers())

    def __get_headers(self):
        """
        Get default headers for API requests.
        """
        return {
            "User-Agent": USER_AGENT,
            "X-Requested-With": "com.playtomic.web",
        }

    def login(self) -> AuthPayload:
        """
        Login to Playtomic API.
        """
        url = f"{AUTH_URL}/auth/login"
        data = {"email": self.email, "password": self.password}

        # Make HTTP request
        response = self.session.post(url, json=data, timeout=5)
        response.raise_for_status()
        response: AuthPayload = response.json()

        # Get user ID and access token
        self.access_token = response.get("access_token")
        self.user_id = response.get("user_id")

        # Set authorization header
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

        return response

    def fetch_availability(self, tenant_id, start_date, end_date):
        """
        Fetch the availability for a given tenant (court).
        """
        if not self.access_token:
            self.login()

        url = f"{API_URL}/availability"
        params = {
            "user_id": "me",
            "tenant_id": tenant_id,
            "sport_id": "PADEL",
            "local_start_min": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "local_start_max": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        # Make HTTP request
        response = self.session.get(url, params=params, timeout=5)
        response.raise_for_status()

        return response.json()

    def create_payment_intent(self, data: Dict) -> PaymentIntent:
        """
        Create a payment intent for a given tenant (court).
        """
        if not self.access_token:
            self.login()

        url = f"{API_URL}/payment_intents"

        # Make HTTP request
        response = self.session.post(url, json=data, timeout=5)
        response.raise_for_status()

        return response.json()

    def update_payment_intent(self, payment_intent_id: Text, data: Dict):
        """
        Update the payment intent.
        """
        if not self.access_token:
            self.login()

        url = f"{API_URL}/payment_intents/{payment_intent_id}"

        # Make HTTP request
        response = self.session.patch(url, json=data, timeout=5)
        response.raise_for_status()

        return response.json()

    def confirm_reservation(self, payment_intent_id: Text):
        """
        Confirm a reservation.
        """
        if not self.access_token:
            self.login()

        url = f"{API_URL}/payment_intents/{payment_intent_id}/confirmation"

        # Make HTTP request
        response = self.session.post(url, timeout=5)
        response.raise_for_status()

        return response.json()

    def prepare_payment_intent_data(
        self,
        tenant_id: Text,
        resource_id: Text,
        start_date: datetime,
        duration: float,
    ):
        """
        Prepare the payment intent data.
        """
        # Prepare data
        utc_start_date = start_date.astimezone(pytz.utc)
        return {
            "allowed_payment_method_types": [
                "OFFER",
                "CASH",
                "MERCHANT_WALLET",
                "DIRECT",
                "SWISH",
                "IDEAL",
                "BANCONTACT",
                "PAYTRAIL",
                "CREDIT_CARD",
                "QUICK_PAY",
            ],
            "user_id": self.user_id,
            "cart": {
                "requested_item": {
                    "cart_item_type": "CUSTOMER_MATCH",
                    "cart_item_voucher_id": None,
                    "cart_item_data": {
                        "supports_split_payment": True,
                        "number_of_players": 4,
                        "tenant_id": tenant_id,
                        "resource_id": resource_id,
                        "start": utc_start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "duration": duration,
                        "match_registrations": [
                            {"user_id": self.user_id, "pay_now": True}
                        ],
                    },
                }
            },
        }
