import msal
import requests
import os
from dotenv import load_dotenv
from utils.email_templates import generate_email_body

load_dotenv()

# Load environment variables
# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# TENANT_ID = os.getenv("TENANT_ID")

CLIENT_ID = "7aaaf0f1-7c37-424e-a9ed-397f9df6d375"
TENANT_ID = "6eaadc6a-a688-4ff0-abb3-772fb62d75e1"
CLIENT_SECRET = "lLg8Q~Elq7LB~Ic.est7eVsgNk3fL7mkrs5gGcdC"

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
