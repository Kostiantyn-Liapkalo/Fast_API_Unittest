from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator])
access_update = RolesAccess([Role.admin, Role.moderator])
access_delete = RolesAccess([Role.admin])


@router.get("/", response_model=List[ContactResponse],
            dependencies=[Depends(access_get), Depends(RateLimiter(times=2, seconds=5))],
            description='Two requests on 5 seconds',
            name='Get a list of contacts using query parameters: first name, last name, email')
async def get_contacts(limit: int = Query(default=10),
                       offset: int = 0,
                       first_name: Optional[str] = Query(default=None),
                       last_name: Optional[str] = Query(default=None),
                       email: Optional[str] = Query(default=None),
                       db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.
    The function accepts the following parameters:
    limit (int): The number of contacts to return. Defaults to 10 if not specified.
    offset (int): The number of contacts to skip before returning results. Defaults to 0 if not specified.
    first_name (str): A string containing the first name for which you want results returned,
    or None if you don't want this parameter used in your search query.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n contacts
    :param first_name: Optional[str]: Filter the contacts by first name
    :param last_name: Optional[str]: Filter contacts by last name
    :param email: Optional[str]: Filter the contacts by email address
    :param db: Session: Get a database session
    :param user: User: Get the current user
    :return: A list of contacts
    """
    contact = await repository_contacts.get_contacts(limit, offset, first_name, last_name, email, user, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contacts with requested parameters not found")
    return contact


@router.get("/birthdays", response_model=List[ContactResponse],
            dependencies=[Depends(access_get), Depends(RateLimiter(times=2, seconds=5))],
            description='Two requests on 5 seconds',
            name='Get a list of all contacts who has birthday during next 7 days')
async def get_contacts_by_birthday(limit: int = Query(10, le=300), offset: int = 0,
                                   db: Session = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_birthday function returns a list of contacts that have birthdays in the current month.
    The function takes an optional limit and offset parameter to control how many results are returned, as well as
    a user object from the auth_service module. The function uses the search_contacts_by_birthday method from
    the repository module to query for contacts with birthdays in the current month.

    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: Session: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts with a birthday in the next 30 days
    """
    contacts = await repository_contacts.search_contacts_by_birthday(limit, offset, user, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse,
            dependencies=[Depends(access_get), Depends(RateLimiter(times=2, seconds=5))],
            description='Two requests on 5 seconds')
async def get_contact(contact_id: int = Path(ge=1),
                      db: Session = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it raises an HTTP 404 error.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access_create), Depends(RateLimiter(times=2, seconds=5))],
             description='Two requests on 5 seconds')
async def create_contact(body: ContactModel,
                         db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the repository
    :param user: User: Get the current user
    :return: The newly created contact object
    """
    contact = await repository_contacts.create(body, user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse,
            dependencies=[Depends(access_update)])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
    The function takes an id, body and db as parameters.
    It returns a ContactModel object.

    :param body: ContactModel: Pass the contact data to the function
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Get the database session
    :param user: User: Get the current user
    :return: A contactmodel object
    """
    contact = await repository_contacts.update(contact_id, body, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access_delete)])
async def delete_contact(contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to be deleted
    :param db: Session: Get a database session
    :param user: User: Get the current user from the database
    :return: None
    """
    contact = await repository_contacts.remove(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return None
