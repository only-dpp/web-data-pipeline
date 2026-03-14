from pydantic import BaseModel, EmailStr


class DigestSendRequest(BaseModel):
    to_email: EmailStr
    hours: int = 24
    limit: int = 10