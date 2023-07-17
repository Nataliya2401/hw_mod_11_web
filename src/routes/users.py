from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session


from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserResponse
from src.services.cloud_image import CloudImage

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.

    :param current_user: User: Pass the user object to the function
    :return: The current_user object
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):

    """
    The update_avatar_user function updates the avatar of a user.
    It takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
    :param file: Get the file from the request.
    :type file: UploadFile
    :param current_user: Get the current user from the database.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated user
    """
    public_id = CloudImage.generate_name_file_avatar(current_user.email)
    r = CloudImage.upload(file.file, public_id)
    src_url = CloudImage.get_url_for_avatar(public_id, r)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
