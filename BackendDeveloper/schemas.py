from pydantic import BaseModel, constr


class RegisterRequest(BaseModel):
    identifier: str
    password: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AvatarResponse(BaseModel):
    avatar_url: str


class DeleteResponse(BaseModel):
    message: str


class RegisterData(BaseModel):
    identifier: str
    password: constr(min_length=6, max_length=72)  # bcrypt limit
