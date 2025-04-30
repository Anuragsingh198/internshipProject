from pydantic import BaseModel, EmailStr

class OtpRequest(BaseModel):
    email: EmailStr

class OtpVerify(BaseModel):
    email: EmailStr
    otp: int

class OtpOut(BaseModel):
    message: str
