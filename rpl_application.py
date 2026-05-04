"""
RPL System - RPLApplication and Notification Classes
"""
from datetime import datetime
from typing import List, Optional
from src.module_request import ModuleRequest


class Notification:
    """Represents a notification sent to a student or assessor."""

    VALID_CHANNELS = {"email", "sms", "in-app"}

    def __init__(self, notification_id: str, message: str,
                 recipient_id: str, channel: str = "email"):
        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid channel: {channel}")
        self.__notification_id = notification_id
        self.__message = message
        self.__recipient_id = recipient_id
        self.__channel = channel
        self.__sent_at: Optional[datetime] = None
        self.__is_read: bool = False

    # Getters
    @property
    def notification_id(self): return self.__notification_id
    @property
    def message(self): return self.__message
    @property
    def recipient_id(self): return self.__recipient_id
    @property
    def channel(self): return self.__channel
    @property
    def sent_at(self): return self.__sent_at
    @property
    def is_read(self): return self.__is_read

    def send(self) -> bool:
        """Simulate sending the notification."""
        self.__sent_at = datetime.now()
        return True

    def mark_as_read(self) -> None:
        self.__is_read = True

    def resend(self) -> bool:
        """Resend the notification."""
        self.__sent_at = datetime.now()
        self.__is_read = False
        return True

    def get_notification_details(self) -> dict:
        return {
            "notification_id": self.__notification_id,
            "message": self.__message,
            "recipient_id": self.__recipient_id,
            "channel": self.__channel,
            "sent_at": str(self.__sent_at),
            "is_read": self.__is_read,
        }

    def __repr__(self):
        return (f"Notification(id={self.__notification_id}, "
                f"channel={self.__channel}, read={self.__is_read})")


class RPLApplication:
    """
    Represents a student's RPL application containing one or more module requests.
    Lifecycle: Draft → Pending → UnderReview → Approved | Rejected | PartiallyApproved
    """

    VALID_STATUSES = {
        "Draft", "Pending", "UnderReview",
        "Approved", "Rejected", "PartiallyApproved", "Withdrawn"
    }
    BASE_FEE = 500.00  # Base application fee in ZAR

    def __init__(self, application_id: str, student_id: str):
        self.__application_id = application_id
        self.__student_id = student_id
        self.__submission_date: Optional[datetime] = None
        self.__status: str = "Draft"
        self.__application_fee: float = 0.0
        self.__payment_status: str = "Unpaid"
        self.__last_updated: datetime = datetime.now()
        self.__module_requests: List[ModuleRequest] = []
        self.__notifications: List[Notification] = []

    # Getters
    @property
    def application_id(self): return self.__application_id
    @property
    def student_id(self): return self.__student_id
    @property
    def status(self): return self.__status
    @property
    def submission_date(self): return self.__submission_date
    @property
    def application_fee(self): return self.__application_fee
    @property
    def payment_status(self): return self.__payment_status
    @property
    def module_requests(self): return list(self.__module_requests)

    def add_module_request(self, module_request: ModuleRequest) -> None:
        """Add a module request to this application (composition)."""
        self.__module_requests.append(module_request)

    def submit(self) -> bool:
        """Submit the application. Requires at least one module request (BR-002)."""
        if not self.__module_requests:
            raise ValueError("BR-002: Application must contain at least one module request.")
        self.__status = "Pending"
        self.__submission_date = datetime.now()
        self.__application_fee = self.calculate_fee()
        self.__last_updated = datetime.now()
        self._send_notification(f"Your RPL application {self.__application_id} has been submitted.")
        return True

    def withdraw(self) -> bool:
        """Withdraw application. Only allowed in Pending or UnderReview (BR-004)."""
        if self.__status not in ("Pending", "UnderReview"):
            raise ValueError(
                f"BR-004: Cannot withdraw application in '{self.__status}' status."
            )
        self.__status = "Withdrawn"
        self.__last_updated = datetime.now()
        self._send_notification(f"Your RPL application {self.__application_id} has been withdrawn.")
        return True

    def update_status(self, new_status: str) -> None:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        self.__status = new_status
        self.__last_updated = datetime.now()
        self._send_notification(
            f"Your application {self.__application_id} status updated to: {new_status}"
        )

    def calculate_fee(self) -> float:
        """Fee based on number of module requests."""
        return self.BASE_FEE + (len(self.__module_requests) * 150.0)

    def get_application_summary(self) -> str:
        return (
            f"Application [{self.__application_id}] | Student: {self.__student_id} | "
            f"Status: {self.__status} | Modules: {len(self.__module_requests)} | "
            f"Fee: R{self.__application_fee:.2f} | Payment: {self.__payment_status}"
        )

    def _send_notification(self, message: str) -> None:
        notif_id = f"NOTIF-{self.__application_id}-{len(self.__notifications) + 1}"
        notification = Notification(notif_id, message, self.__student_id, "email")
        notification.send()
        self.__notifications.append(notification)

    def get_notifications(self) -> List[Notification]:
        return list(self.__notifications)

    def __repr__(self):
        return (f"RPLApplication(id={self.__application_id}, "
                f"student={self.__student_id}, status={self.__status})")
