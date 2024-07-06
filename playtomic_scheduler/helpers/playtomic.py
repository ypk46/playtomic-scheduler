# Native imports
from typing import Text
from datetime import datetime
from typing_extensions import TypedDict

# 3rd party imports
import requests


class AuthPayload(TypedDict):
    access_token: Text
    access_token_expiration: Text
    refresh_token: Text
    refresh_token_expriation: Text
    user_id: Text


class Playtomic:
    # Constants
    API_URL = "https://playtomic.io/api/v1"
    AUTH_URL = "https://playtomic.io/api/v3"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )

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
            "User-Agent": self.USER_AGENT,
            "X-Requested-With": "com.playtomic.web",
        }

    def login(self) -> AuthPayload:
        """
        Login to Playtomic API.
        """
        url = f"{self.AUTH_URL}/auth/login"
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

        url = f"{self.API_URL}/availability"
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

    def create_payment_intent(
        self,
        tenant_id: Text,
        resource_id: Text,
        start_date: datetime,
        duration: float,
    ):
        """
        Create a payment intent for a given tenant (court).
        """
        if not self.access_token:
            self.login()

        url = f"{self.API_URL}/payment_intents"

        # Make HTTP request
        response = self.session.get(url, timeout=5)
        response.raise_for_status()

        return response.json()
