from typing import Optional

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from src.database.models import Role


class ContactModel(BaseModel):
    first_name: str = Field('Taras', min_length=3, max_length=16)
    last_name: str = Field('Shevchenko', min_length=3, max_length=16)
    email: str = Field('Shevchenko@ukr.net', min_length=10, max_length=150)
    phone_number: str = Field('+380671112233', min_length=9, max_length=16)
    birthday: str = Field('1814-03-09')
    additional_data: str


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str = Field('Taras', min_length=3, max_length=16)
    last_name: str = Field('Shevchenko', min_length=3, max_length=16)
    email: str = Field('Shevchenko@ukr.net', min_length=10, max_length=150)
    phone_number: str = Field('+380671112233', min_length=9, max_length=16)
    birthday: str = Field('1814-03-09')
    additional_data: str

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=30)
    email: str = Field('Shevchenko@ukr.net', min_length=10, max_length=150)
    password: str = Field(min_length=6, max_length=30)


class UserResponse(BaseModel):
    id: int
    username: str = Field(min_length=5, max_length=30)
    email: str = Field('Shevchenko@ukr.net', min_length=10, max_length=150)
    avatar: str
    role: Role

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: str = Field('Shevchenko@ukr.net', min_length=10, max_length=150)