from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


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
