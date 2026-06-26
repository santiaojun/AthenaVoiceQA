import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

def make_call(webhook_url: str):
    call = client.calls.create(
        to=os.getenv("TARGET_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        url=f"{webhook_url}/answer",
        record=True,
        status_callback=f"{webhook_url}/hangup",
        status_callback_event=["completed"],
    )
    print(f"Call SID: {call.sid}")
    return call.sid

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python caller.py <ngrok_url>")
        sys.exit(1)
    webhook_url = sys.argv[1]
    make_call(webhook_url)