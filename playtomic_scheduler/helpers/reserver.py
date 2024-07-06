# Native imports
import logging
from typing import List, Dict, Text
from datetime import datetime, timedelta

# Project imports
from playtomic_scheduler.utils import date
from .playtomic import Playtomic

logger = logging.getLogger("playtomic-scheduler-cli")

# Constants
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Reserver:
    playtomic: Playtomic
    days: List[int]
    hours: str
    duration: float
    reservation_confirmed = False

    def __init__(
        self,
        playtomic: Playtomic,
        target_days: str,
        target_hours: str,
        target_duration: str,
    ):
        self.playtomic = playtomic
        self.days = self.__parse_target_days(target_days)
        self.hours = target_hours
        self.duration = float(target_duration)

    def __parse_target_days(self, days: str):
        """
        Parse the desired days to reserve courts.
        """
        days = days.split(",")
        if not isinstance(days, list):
            raise ValueError(
                "Days must be provided as numeric days separated by commas."
            )

        return [int(d) - 1 for d in days]

    def __parse_target_dates(self, base_date: datetime):
        """
        Parse the target hour to reserve courts.
        """
        hours = self.hours.split(",")
        if not isinstance(hours, list):
            raise ValueError(
                "Hours must be provided as a string of hours separated by commas."
            )

        # Parse target hours as datetime objects
        target_dates = []

        for hour in hours:
            target_date = date.parse_datetime(hour, base_date)
            target_dates.append(target_date)

        return target_dates

    def process_tenant(self, tenant: dict):
        """
        Process the tenant and reserve the court.
        """
        tenant_id = tenant.get("id")
        tenant_name = tenant.get("name")
        logger.info("Verifying courts for %s...", tenant_name)

        # Setup start and end date
        start_date = date.set_start_of_day(datetime.now())
        end_date = date.set_end_of_day(datetime.now())
        search_date_limit = datetime.now() + timedelta(days=7)

        while start_date < search_date_limit:
            # Fetch availability
            availability_entries = self.playtomic.fetch_availability(
                tenant_id,
                start_date,
                end_date,
            )

            # Process each availability entry
            logger.info("Looking courts at %s...", start_date.strftime("%Y-%m-%d"))
            for entry in availability_entries:
                self.process_availibility(entry, tenant_id)

            # Increment the dates
            start_date += timedelta(days=1)
            end_date += timedelta(days=1)

    def process_availibility(self, entry: Dict, tenant_id: str):
        """
        Process the availability entries.
        """
        resource_id = entry.get("resource_id")
        start_date_str = entry.get("start_date")

        # Process each slot
        for slot in entry.get("slots"):
            # Validate court duration
            slot_duration = slot.get("duration")
            if slot_duration != self.duration * 60:
                continue

            # Validate court start time
            slot_time = slot["start_time"]
            slot_start_date_str = f"{start_date_str} {slot_time}"
            slot_start_date = datetime.strptime(slot_start_date_str, DATE_FORMAT)
            slot_start_date = date.parse_utc_to_local(slot_start_date)

            # Check if the slot is within the target hours
            target_dates = self.__parse_target_dates(slot_start_date)
            if slot_start_date not in target_dates:
                continue

            readable_date = slot_start_date.strftime("%Y %b %d - %I:%M %p")
            logger.info("Found a valid court: %s", readable_date)

            # Check if matches target days
            if (
                slot_start_date.weekday() in self.days
                and not self.reservation_confirmed
            ):
                self.reserve_court(tenant_id, resource_id, slot_start_date)

    def reserve_court(self, tenant_id: Text, resource_id: Text, start_date: datetime):
        """
        Reserve the court.
        """
        data = self.playtomic.prepare_payment_intent_data(
            tenant_id,
            resource_id,
            start_date,
            self.duration * 60,
        )

        # Create payment intent
        payment_intent = self.playtomic.create_payment_intent(data)

        # Update payment intent
        payment_methods = payment_intent.get("available_payment_methods")
        payment_method = next(
            (
                method
                for method in payment_methods
                if method["name"] == "Pay at the club"
            ),
            None,
        )
        data = {
            "selected_payment_method_id": payment_method.get("payment_method_id"),
            "selected_payment_method_data": None,
        }
        self.playtomic.update_payment_intent(payment_intent.get("id"), data)

        # Confirm reservation
        self.playtomic.confirm_reservation(payment_intent.get("id"))

        logger.info(
            "Reservation confirmed on %s", start_date.strftime("%Y %b %d - %I:%M %p")
        )
        self.reservation_confirmed = True
