# Native imports
import re
import json
import base64
import logging
from datetime import datetime
from typing import Text, Dict, List
from typing_extensions import TypedDict

# 3rd party imports
import pytz
import requests

logger = logging.getLogger("playtomic-scheduler-cli")

# Constants
API_URL = "https://playtomic.com/api"
AUTH_URL = "https://app.playtomic.com"
LOGIN_URL = f"{AUTH_URL}/login"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
)


class AuthPayload(TypedDict):
    access_token: Text
    refresh_token: Text
    user_id: Text


class PaymentIntent(TypedDict):
    payment_intent_id: Text
    available_payment_methods: List


class Match(TypedDict):
    match_id: Text
    start_date: Text
    status: Text


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
        self.access_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    @staticmethod
    def __decode_jwt_payload(token: Text) -> Dict:
        """Decode the payload from a JWT token without verification."""
        # JWT structure: header.payload.signature
        payload_b64 = token.split(".")[1]
        # Add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)

    def __fetch_login_action_params(self) -> Dict[Text, Text]:
        """Fetch the login page and extract Next.js Server Action parameters.

        The login page contains hidden form fields with the action ID and key
        that are generated at build time. This method scrapes them dynamically
        so they don't need to be hardcoded.
        """
        response = self.session.get(LOGIN_URL, timeout=10)
        response.raise_for_status()
        html = response.text

        # Extract ACTION_ID from: name="$ACTION_1:0" value='{"id":"<ACTION_ID>",...}'
        action_id_match = re.search(
            r'name="\$ACTION_1:0"[^>]*value="([^"]*)"', html
        )
        if not action_id_match:
            raise ValueError("Could not find ACTION_ID on the login page.")

        # The value is HTML-encoded JSON, decode &quot; -> "
        action_value = action_id_match.group(1).replace("&quot;", '"')
        action_data = json.loads(action_value)
        action_id = action_data["id"]

        # Extract ACTION_KEY from: name="$ACTION_KEY" value="<ACTION_KEY>"
        action_key_match = re.search(
            r'name="\$ACTION_KEY"[^>]*value="([^"]*)"', html
        )
        if not action_key_match:
            raise ValueError("Could not find ACTION_KEY on the login page.")

        action_key = action_key_match.group(1)

        logger.info("Fetched login action params: id=%s, key=%s", action_id, action_key)
        return {"action_id": action_id, "action_key": action_key}

    def login(self) -> AuthPayload:
        """Login to Playtomic via the app.playtomic.com login endpoint."""
        # Dynamically fetch the Next.js action ID and key from the login page
        action_params = self.__fetch_login_action_params()
        action_id = action_params["action_id"]
        action_key = action_params["action_key"]

        url = f"{LOGIN_URL}?return_url=https%3A%2F%2Fplaytomic.com%2F"

        # Build multipart form fields matching the Next.js Server Action format
        action_ref = json.dumps({"id": action_id, "bound": "$@1"})
        action_bound = json.dumps(
            [{"action": "login", "returnURL": "https://playtomic.com/",
              "callbackURL": "$undefined"}]
        )
        form_fields = {
            "1_$ACTION_REF_1": (None, ""),
            "1_$ACTION_1:0": (None, action_ref),
            "1_$ACTION_1:1": (None, action_bound),
            "1_$ACTION_KEY": (None, action_key),
            "1_type": (None, "credentials"),
            "1_email": (None, self.email),
            "1_password": (None, self.password),
            "0": (
                None,
                json.dumps(
                    [{"action": "login", "returnURL": "https://playtomic.com/",
                      "callbackURL": "$undefined"}, "$K1"]
                ),
            ),
        }

        headers = {
            "Accept": "text/x-component",
            "Next-Action": action_id,
            "Origin": AUTH_URL,
            "Referer": url,
        }

        # POST login, do not follow the 303 redirect automatically
        response = self.session.post(
            url, files=form_fields, headers=headers,
            allow_redirects=False, timeout=10,
        )

        # Expect a 303 redirect on successful login
        if response.status_code not in (303, 200):
            response.raise_for_status()

        # Extract auth tokens from cookies set by the response
        self.access_token = self.session.cookies.get(
            "pt_auth_access_token", domain=".playtomic.com"
        )
        refresh_token = self.session.cookies.get(
            "pt_auth_refresh_token", domain=".playtomic.com"
        )

        if not self.access_token:
            raise ValueError("Login failed: no access token cookie received.")

        # Decode user_id from JWT payload
        jwt_payload = self.__decode_jwt_payload(self.access_token)
        self.user_id = jwt_payload.get("sub")

        logger.info("Logged in successfully as user %s", self.user_id)

        return {
            "access_token": self.access_token,
            "refresh_token": refresh_token,
            "user_id": self.user_id,
        }

    def fetch_availability(self, tenant_id: Text, target_date: datetime) -> List:
        """Fetch the availability for a given tenant (court) on a specific date."""
        if not self.access_token:
            self.login()

        url = f"{API_URL}/clubs/availability"
        params = {
            "tenant_id": tenant_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "sport_id": "PADEL",
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

    def get_matches(self, size: int, sort: Text) -> List[Match]:
        """
        Get list of matches.
        """
        if not self.access_token:
            self.login()

        url = f"{API_URL}/matches"
        params = {"size": str(size), "sort": sort, "owner_id": self.user_id}

        # Make HTTP request
        response = self.session.get(url, params=params, timeout=5)
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
