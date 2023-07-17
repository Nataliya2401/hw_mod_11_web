from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    """
    The get_contacts function returns a list of contacts created current user.

    :param limit: Limit the number of contacts returned.
    :type limit: int
    :param offset: Determine how many contacts to skip before returning the results.
    :type offset: int
    :param user: Get the user from the database.
    :type user: User
    :param db: Database session.
    :type db: Session
    :return: All contacts for the user.
    :rtype: List[Contact]
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    The get_contact_by_id function takes in a contact_id and user, and returns the contact with that id.

    If not contact with such id, return None

    :param contact_id: int: Specify the id of the contact we want to get
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session object to the function
    :return: The contact with the specified id
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_email(email: str, user: User, db: Session):
    """
    The get_contact_by_email function takes in an email and returns the contact with that email.
    The search for contacts will be among the contacts of a specific user

    :param email: str: Filter the contact by email
    :param user: User: Get the user id from the database
    :param db: Session
    :return: A contact object created the user and with the email
    """
    contact = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).first()
    return contact


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    The create_contact function creates a new contact in the database for the specific user

    :param body: ContactModel: contact info
    :param user: User: Current user
    :param db: Session
    :return: The contact object
    """
    contact = Contact(**body.dict())
    contact.user_id = user.id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session):
    """
    The update_contact function updates a contact with the contact_id in the database.

    :param body: ContactModel:  The updated data for the contact
    :param contact_id: int: the contact id
    :param user: User: Current user
    :param db: Session: Pass a database session to the function
    :return: The updated contact
    """
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
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact. Only contacts belonging to this user can be removed.
            db (Session): A connection to our database.

    :param contact_id: int: Identify the contact to be removed
    :param user: User: Get the user's id
    :param db: Session: Pass a database session to the function
    :return: A contact object or None
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_contacts_by_name(firstname: str | None, lastname: str | None, user: User, db: Session):
    """
    The find_contacts_by_name function takes in a firstname or lastname, as well as the user who is making the request
    and the database session.

    :param firstname: str | None: Find the contact by the firstname if you know it
    :param lastname: str | None: Find the contact by lastname if you know it
    :param user: User: Current user
    :param db: Session: Create a connection to the database
    :return: A list of contacts created by current user, that match the first name or last name.
    :rtype: List[Contact]
    """
    contact = db.query(Contact).filter(
        and_(or_(Contact.firstname.ilike(f"%{firstname}%"), Contact.lastname.ilike(f"%{lastname}%")),
             Contact.user_id == user.id)).all()
    # contact = db.query(Contact).filter(or_(Contact.firstname == firstname, Contact.lastname == lastname)).all()
    return contact


async def birthday_people(limit: int, offset: int, user: User, db: Session):
    """
    The birthday_people function returns a list of contacts whose birthday is within the next 7 days.
    The search for contacts will be among the contacts of a specific user

    :param limit: int: Limit the number of contacts that are returned
    :param offset: int: Specify the number of records to skip before starting to return the records
    :param user: User: Current user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthday is within 7 days and who created the current user
    """
    current_date = datetime.now().date()
    current_year = current_date.year
    delta = 7
    end_data = current_date + timedelta(days=delta)
    contact = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    # print('gggg', contact)
    list_birthday = []
    for c in contact:
        # print(c.birthday)
        if c.birthday:
            c_birthday_this_year = c.birthday.replace(year=current_year)
            print(c_birthday_this_year)
            if current_date <= c_birthday_this_year <= end_data:
                list_birthday.append(c)
    else:
        print('hhhh')
    return list_birthday
