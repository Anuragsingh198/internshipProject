from pydantic import BaseModel, EmailStr

class OTPRequest(BaseModel):
    email: EmailStr

class OTPResponse(BaseModel):
    message: str

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPVerifyResponse(BaseModel):
    message: str
