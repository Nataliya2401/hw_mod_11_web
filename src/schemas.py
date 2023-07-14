from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from src.database.models import Role


class ContactModel(BaseModel):
    firstname: str = Field(min_length=2, max_length=50)
    lastname: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=4, max_length=20)
    birthday: Optional[date] = None
    additionally: str


class ContactResponse(BaseModel):
    id: int = 1
    email: EmailStr
    firstname: str
    lastname: str
    phone: str
    birthday: Optional[date] = None
    additionally: str

    class Config:
        orm_mode = True

# Встановлення цього параметру - показує, що валідувати треба дані, які йдуть з БД, тобто дані треба брати з БД
# Якщо треба валідувати дані не з БД, то цей параметр не встановлюється


class UserModel(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    detail: str = "User successfully created"
    avatar: str
    roles: Role

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr

