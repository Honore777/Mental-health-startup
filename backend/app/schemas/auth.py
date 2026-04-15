from pydantic import BaseModel, EmailStr, Field


class ProfessionalDetailsIn(BaseModel):
    specialization: str
    bio: str
    price: float = Field(gt=0)
    availability: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    role: str = "user"
    professional_details: ProfessionalDetailsIn | None = Field(default=None, alias="professionalDetails")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str | None
    role: str


class AuthResponse(BaseModel):
    user: UserOut
