import msal
import requests
from utils.email_templates import generate_email_body
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

print(TENANT_ID , CLIENT_ID , CLIENT_SECRET)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
SENDER_EMAIL = "technical_user@ielektron.com"  


app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)



def send_email(recipient_email: str, subject: str, purpose: str, **kwargs) -> bool:
    try:
        token_result = app.acquire_token_for_client(scopes=SCOPE)
        if "access_token" not in token_result:
            print("❌ Token Error:", token_result.get("error_description"))
            return False

        access_token = token_result["access_token"]
        email_body = generate_email_body(purpose, **kwargs)

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": email_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email
                        }
                    }
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail",
            headers=headers,
            json=message
        )

        if response.status_code == 202:
            print(f"✅ Email sent to {recipient_email}")
            return True
        else:
            print(f"❌ Failed to send email ({response.status_code}):", response.json())
            return False

    except Exception as e:
        print("❌ Exception occurred while sending email:", str(e))
        return False
