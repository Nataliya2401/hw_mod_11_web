from typing import List

from fastapi import Path, Query, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repo_contacts
from src.schemas import ContactModel, ContactResponse

router = APIRouter(prefix="/contacts", tags=['contacts'])


@router.get("/", response_model=List[ContactResponse], name="=====My Contacts:=====")
async def get_contacts(limit: int = Query(10, le=100), offset: int = 0, db: Session = Depends(get_db)):
    contacts = await repo_contacts.get_contacts(limit, offset, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repo_contacts.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/email/{contact_email}", response_model=ContactResponse)
async def get_contact_e(contact_email: str = Path(..., description='Enter email'), db: Session = Depends(get_db)):
    contact = await repo_contacts.get_contact_by_email(contact_email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/find/", response_model=List[ContactResponse], name="==Find  Contacts by name ====")
async def find_contacts_by_name(first_name: str | None = Query(None, description='First Name'),
                                last_name: str | None = None,
                                db: Session = Depends(get_db)):
    print(first_name, last_name)
    contacts = await repo_contacts.find_contacts_by_name(first_name, last_name, db)
    return contacts


@router.get("/birthday/", response_model=List[ContactResponse], name="Contacts with birthday in the next 7 days")
async def birthday_people(limit: int = Query(10, le=100), offset: int = 0, db: Session = Depends(get_db)):
    contacts = await repo_contacts.birthday_people(limit, offset, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    contact = await repo_contacts.get_contact_by_email(body.email, db)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is exist')

    contact = await repo_contacts.create_contact(body, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repo_contacts.update_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repo_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact

# @router.patch("/{contact_id}/vaccinated", response_model=CatResponse)
# async def vaccinated_cat(body: VaccinatedCatModel, cat_id: int = Path(ge=1), db: Session = Depends(get_db)):
#     cat = db.query(Cat).filter_by(id=cat_id).first()
#     if cat is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
#     cat.vaccinated = body.vaccinated
#     db.commit()
#     return cat
