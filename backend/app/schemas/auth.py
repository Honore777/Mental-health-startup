from pydantic import BaseModel, EmailStr, Field, field_validator


MAX_BCRYPT_PASSWORD_BYTES = 72


def _validate_password_length(value: str) -> str:
    if len(value.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password is too long. Maximum supported length is 72 UTF-8 bytes.")
    return value


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

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        return _validate_password_length(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        return _validate_password_length(value)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str | None
    role: str


class AuthResponse(BaseModel):
    user: UserOut
