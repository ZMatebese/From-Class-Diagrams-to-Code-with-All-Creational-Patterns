"""
Creational Pattern 1: Simple Factory
======================================
Pattern: Simple Factory
Use Case: Centralised creation of different RPL-related objects.
           Instead of callers needing to know constructor details,
           they ask the factory for the object type they need.

RPL Context:
  RPLObjectFactory creates Notification objects for different channels
  (email, sms, in-app) and RPLApplication objects — hiding constructor
  complexity from the rest of the system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rpl_application import RPLApplication, Notification


class RPLObjectFactory:
    """
    Simple Factory: one class with a static method that decides which
    concrete object to instantiate based on a type string.
    """

    @staticmethod
    def create_notification(notif_type: str, notification_id: str,
                            message: str, recipient_id: str) -> Notification:
        """
        Create a Notification with the appropriate channel.

        Args:
            notif_type: 'email' | 'sms' | 'in-app'
            notification_id: Unique ID
            message: Notification body
            recipient_id: Recipient's ID

        Returns:
            Notification instance configured for the given channel
        """
        valid_types = {"email", "sms", "in-app"}
        if notif_type not in valid_types:
            raise ValueError(
                f"Unknown notification type '{notif_type}'. "
                f"Valid types: {valid_types}"
            )
        return Notification(notification_id, message, recipient_id, channel=notif_type)

    @staticmethod
    def create_application(app_type: str, application_id: str,
                           student_id: str) -> RPLApplication:
        """
        Create an RPLApplication. Future expansion could support
        'standard', 'expedited', or 'appeal' types with different fee rules.

        Args:
            app_type: 'standard' | 'expedited' | 'appeal'
            application_id: Unique application ID
            student_id: Applicant's student ID

        Returns:
            RPLApplication instance
        """
        valid_types = {"standard", "expedited", "appeal"}
        if app_type not in valid_types:
            raise ValueError(
                f"Unknown application type '{app_type}'. "
                f"Valid types: {valid_types}"
            )
        # All types create the same class; type influences fee logic in practice
        app = RPLApplication(application_id, student_id)
        return app


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Simple Factory Demo ===\n")

    # Create email notification
    email_notif = RPLObjectFactory.create_notification(
        "email", "N001", "Your application has been received.", "STU-001"
    )
    print(f"Created: {email_notif}")

    # Create SMS notification
    sms_notif = RPLObjectFactory.create_notification(
        "sms", "N002", "RPL update: Under Review.", "STU-001"
    )
    print(f"Created: {sms_notif}")

    # Create in-app notification
    inapp_notif = RPLObjectFactory.create_notification(
        "in-app", "N003", "Action required: Upload missing evidence.", "STU-002"
    )
    print(f"Created: {inapp_notif}")

    # Create standard application
    app = RPLObjectFactory.create_application("standard", "APP-101", "STU-001")
    print(f"\nCreated: {app}")

    # Invalid type raises error
    try:
        RPLObjectFactory.create_notification("fax", "N004", "msg", "STU-003")
    except ValueError as e:
        print(f"\nExpected error: {e}")
