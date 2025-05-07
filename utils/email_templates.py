def generate_email_body(purpose: str, **kwargs) -> str:
    if purpose == "otp":
        return f"""
        Hello,

        Your One-Time Password (OTP) for verification is: 🔐 {kwargs.get('otp')}

        This OTP is valid for a short time. Please do not share it with anyone.

        Best regards,  
        DigiVidya Team
        """.strip()

    elif purpose == "project_status":
        return f"""
        Hello,

        This is to inform you of your project status update.

        📌 Status: {kwargs.get('status')}
        📝 Description: {kwargs.get('description')}

        Best regards,  
        DigiVidya Team
        """.strip()

    elif purpose == "project_query":
        return f"""
        Hello,

        Your project query has been received.

        📨 Subject: {kwargs.get('subject')}
        📝 Message: {kwargs.get('message')}

        We will get back to you shortly.

        Best regards,  
        DigiVidya Team
        """.strip()

    else:
        return f"""
        Hello,

        This is a notification from DigiVidya.

        Best regards,  
        DigiVidya Team
        """.strip()
