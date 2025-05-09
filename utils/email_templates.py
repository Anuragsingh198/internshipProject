def otp_email_template(otp: str) -> str:
    return f"""
    Hello,

    Your One-Time Password (OTP) for verification is: 🔐 {otp}

    This OTP is valid for a short time. Please do not share it with anyone.

    Best regards,  
    DigiVidya Team
    """.strip()


def project_status_template(status: str, description: str) -> str:
    return f"""
    Hello,

    This is to inform you of your project status update.

    📌 Status: {status}
    📝 Description: {description}

    Best regards,  
    DigiVidya Team
    """.strip()


def project_assigned_template(project_name: str, assigned_by: str) -> str:
    return f"""
    Hello,

    You have been assigned a new project.

    📁 Project Name: {project_name}
    👤 Assigned By: {assigned_by}

    Please log in to your dashboard for more details.

    Best regards,  
    DigiVidya Team
    """.strip()


def generate_email_body(purpose: str, **kwargs) -> str:
    if purpose == "otp":
        return otp_email_template(kwargs.get("otp", ""))
    elif purpose == "project_status":
        return project_status_template(
            kwargs.get("status", ""), kwargs.get("description", "")
        )
    elif purpose == "project_assigned":
        return project_assigned_template(
            kwargs.get("project_name", ""), kwargs.get("assigned_by", "")
        )
    else:
        return """
        Hello,

        This is a notification from DigiVidya.

        Best regards,  
        DigiVidya Team
        """.strip()
