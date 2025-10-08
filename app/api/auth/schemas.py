from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    """
    Request model for user registration.
    """
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="A valid email address for the user."
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=25,
        example="strongpassword123",
        description="Password must be at least 8 characters long."
    )


class LoginRequest(BaseModel):
    """
    Request model for user login.
    """
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Registered email address."
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        example="strongpassword123",
        description="User's account password."
    )


class TokenResponse(BaseModel):
    """
    Response model for access tokens.
    """
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT access token."
    )
    token_type: str = Field(
        default="bearer",
        example="bearer",
        description="Type of the token, usually 'bearer'."
    )

