from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    contacts = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_email(email: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).first()
    return contact


async def create_contact(body: ContactModel, user: User, db: Session):
    contact = Contact(**body.dict())
    contact.user_id = user.id
    print(contact.firstname, contact.user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.email = body.email
        contact.birthday = body.birthday
        contact.additionally = body.additionally
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_contacts_by_name(firstname: str | None, lastname: str | None, user: User, db: Session):
    contact = db.query(Contact).filter(
        and_(or_(Contact.firstname.ilike(f"%{firstname}%"), Contact.lastname.ilike(f"%{lastname}%")),
             Contact.user_id == user.id)).all()
    # contact = db.query(Contact).filter(or_(Contact.firstname == firstname, Contact.lastname == lastname)).all()
    return contact


async def birthday_people(limit: int, offset: int, user: User, db: Session):
    current_date = datetime.now().date()
    current_year = current_date.year
    delta = 7
    end_data = current_date + timedelta(days=delta)
    contact = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    list_birthday = []
    for c in contact:
        if c.birthday:
            c_birthday_this_year = c.birthday.replace(year=current_year)
            # print(c_birthday_this_year)
            if current_date <= c_birthday_this_year <= end_data:
                list_birthday.append(c)
    return list_birthday
