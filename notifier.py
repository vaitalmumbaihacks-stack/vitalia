import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()


class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")

        if self.account_sid and self.auth_token and self.from_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("Twilio Client Initialized")
            except Exception as e:
                print(f"Error initializing Twilio client: {e}")
                self.client = None
        else:
            print("Twilio credentials missing in .env")
            self.client = None

    def send_whatsapp_message(self, body, to_number):
        if not self.client:
            return False, "Twilio client not initialized. Check credentials."

        try:
            # Ensure numbers are in whatsapp format
            from_whatsapp = f"whatsapp:{self.from_number}"
            to_whatsapp = f"whatsapp:{to_number}"

            message = self.client.messages.create(
                body=body,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            return True, f"Message sent! SID: {message.sid}"
        except Exception as e:
            return False, f"Failed to send message: {str(e)}"
