from typing import List

from fastapi import Path, Query, Depends, HTTPException, status, APIRouter
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import contacts as repo_contacts
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.schemas import ContactModel, ContactResponse

router = APIRouter(prefix="/contacts", tags=['contacts'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_post = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=10, seconds=60))],
            name="=====My Contacts:=====")
async def get_contacts(limit: int = Query(10, le=100), offset: int = 0,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts for the current user.
    The limit and offset parameters are used to paginate the results.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset of the first contact to return
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    contacts = await repo_contacts.get_contacts(limit, offset, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    The function takes in an optional parameter of contact_id, which is an integer greater than or equal to 1.
    It also takes in two dependencies: current_user and db.

    :param contact_id: int: Specify the path parameter for the contact_id
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object, which is a pydantic model
    """
    contact = await repo_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/email/{contact_email}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact_e(contact_email: str = Path(..., description='Enter email'),
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The get_contact_e function returns a contact by email.
        The function takes in an email and returns the contact with that email.

    :param contact_email: str: Email of the contact
    :param current_user: User: Current user
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = await repo_contacts.get_contact_by_email(contact_email, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/find/", response_model=List[ContactResponse], dependencies=[Depends(allowed_operation_get)],
            name="==Find  Contacts by name ====")
async def find_contacts_by_name(first_name: str | None = Query(None, description='First Name'),
                                last_name: str | None = None,
                                current_user: User = Depends(auth_service.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The find_contact_by_name function is used to find contacts in the database.
        It can be filtered by firstname or lastname.
        The current_user parameter is a dependency that will be injected automatically when the function runs.

    :param first_name: str | None: Filter contacts by firstname
    :param last_name: str | None: Filter contacts by lastname
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contacts
    """
    contacts = await repo_contacts.find_contacts_by_name(first_name, last_name, current_user, db)
    return contacts


@router.get("/birthday/", response_model=List[ContactResponse], dependencies=[Depends(allowed_operation_get)],
            name="Contacts with birthday in the next 7 days")
async def birthday_people(limit: int = Query(10, le=100), offset: int = 0,
                          current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    """
    The birthday_people function returns a list of contacts with birthdays in the next 7 days.
        The function takes an optional user parameter, which is used to filter the results by owner.
        If no user is provided, all contacts are returned.

    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: A list of contacts that have birthdays in the next 7 days
    """
    contacts = await repo_contacts.birthday_people(limit, offset, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, dependencies=[Depends(allowed_operation_post)],
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactsModel: Get the data from the request body
    :param current_user: User: Get the user who is currently authorised
    :param db: Session: Get the database session
    :return: A ContactModel object, which is the same as the one in models
    """
    contact = await repo_contacts.get_contact_by_email(body.email, current_user, db)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is exist')

    contact = await repo_contacts.create_contact(body, current_user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - body: A ContactsModel object containing the new data for the contact.
            - contact_id: An integer representing the ID of an existing Contact to be updated.
            - current_user (optional): A User object representing a user who is logged in and making this request.  This argument is optional because it depends on auth_service, which may or may not return a value depending on whether authentication succeeds or fails.

    :param body: ContactsModel: Pass the contact data to be updated
    :param contact_id: int: Specify the contact to be deleted
    :param current_user: User: Get the user id of the current authorised user
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object
    """
    contact = await repo_contacts.update_contact(body, contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_remove)],
               description='Only for admin user')
async def remove_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            current_user (User): The user who is making this request.
            db (Session): A session object
    :param contact_id: int: Specify the contact to be removed
    :param current_user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the repository
    :return: A contact object
    """
    contact = await repo_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
