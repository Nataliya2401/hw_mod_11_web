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
    contacts = await repo_contacts.get_contacts(limit, offset, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    contact = await repo_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/email/{contact_email}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact_e(contact_email: str = Path(..., description='Enter email'),
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
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
    print(first_name, last_name)
    contacts = await repo_contacts.find_contacts_by_name(first_name, last_name, current_user, db)
    return contacts


@router.get("/birthday/", response_model=List[ContactResponse], dependencies=[Depends(allowed_operation_get)],
            name="Contacts with birthday in the next 7 days")
async def birthday_people(limit: int = Query(10, le=100), offset: int = 0,
                          current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    contacts = await repo_contacts.birthday_people(limit, offset, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, dependencies=[Depends(allowed_operation_post)],
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    contact = await repo_contacts.get_contact_by_email(body.email, current_user, db)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is exist')

    contact = await repo_contacts.create_contact(body, current_user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    contact = await repo_contacts.update_contact(body, contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_remove)],
               description='Only for admin user')
async def remove_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    contact = await repo_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
