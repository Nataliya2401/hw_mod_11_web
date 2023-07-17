from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session):
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email. If no such user exists, it returns None.

    :param email: str: Specify the type of parameter that is expected
    :param db: Session: Pass the database session to the function
    :return: The user that matches the email address
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Specify the type of data that will be passed to the function
    :param db: Session: Create a database session
    :return: The new user object
    """
    g = Gravatar(body.email)
    new_user = User(**body.dict(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the refresh token for a user in the database.

    :param user: User: Identify the user that is being updated
    :param refresh_token: Update the user's refresh token in the database
    :param db: Session: Pass the database session to the function
    :return: The user object after updating the refresh_token
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and
    sets the confirmed field of the user with that email to True.

    :param email: str: Specify the email address of the user to be confirmed
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: User email to get user object
    :param url: str: url for new avatar
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user



