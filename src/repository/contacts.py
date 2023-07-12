from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import Contact, User
from src.schemas import ContactModel
from datetime import datetime, timedelta


async def get_contacts(limit: int, offset: int, first_name: str, last_name: str, email: str, user: User, db: Session):
    """
    The get_contacts function returns a list of contacts from the database.
    The function takes in limit, offset, first_name, last_name and email as parameters.
    If all five parameters are provided then it will return a union of three queries: one for each parameter.
    If only four parameters are provided then it will return a union of two queries: one for each pair that is not None.
    If only three or less parameters are provided then it will return the query corresponding to the non-None parameter(s).

    :param limit: int: Specify the number of contacts to return
    :param offset: int: Specify the number of contacts to skip
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter the contacts by email
    :param user: User: Get the user's id from the database
    :param db: Session: Access the database
    :return: A list of contacts
    """
    if first_name:
        first_name = first_name.lower().capitalize()
    if last_name:
        last_name = last_name.lower().capitalize()
    if email:
        email = email.lower()
    first_name_query = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == user.id))
    last_name_query = db.query(Contact).filter(and_(Contact.last_name == last_name, Contact.user_id == user.id))
    email_query = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id))
    if first_name and last_name and email:
        return first_name_query.union(last_name_query).union(email_query).all()
    if first_name and last_name:
        return first_name_query.union(last_name_query).all()
    if first_name and email:
        return first_name_query.union(email_query).all()
    if last_name and email:
        return last_name_query.union(email_query).all()
    if first_name:
        return first_name_query.all()
    if last_name:
        return last_name_query.all()
    if email:
        return email_query.all()
    return db.query(Contact).limit(limit).offset(offset).all()


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    The get_contact_by_id function takes in a contact_id and user, and returns the contact with that id.
    Args:
    contact_id (int): The id of the desired Contact object.
    user (User): The User object associated with this request.

    :param contact_id: int: Get the contact by id
    :param user: User: Get the user_id from the user object
    :param db: Session: Connect to the database
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def search_contacts_by_birthday(limit: int, offset: int, user: User, db: Session):
    """
    The search_contacts_by_birthday function searches for contacts with birthdays in the next 7 days.
    Args:
    limit (int): The number of contacts to return.
    offset (int): The number of contacts to skip before returning results.
    user (User): A User object representing the current user making this request. This is used to filter out other users' data from our search results, so that each user only sees their own data and not anyone else's!

    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the offset of the query
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthdays are in the next 7 days
    """
    today = datetime.today()
    current_year = today.year
    birthdays_in_period = []

    for contact in db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all():
        y, m, d, *_ = contact.birthday.split('-')
        contact_birthday = datetime(year=current_year, month=int(m), day=int(d))

        if today.date() <= contact_birthday.date() <= (today + timedelta(days=7)).date():
            birthdays_in_period.append(contact)
    return birthdays_in_period


async def create(body: ContactModel, user: User, db: Session):
    """
    The create function creates a new contact in the database.

    :param body: ContactModel: Create a new contact object
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: The contact object after it has been created
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user: User, db: Session):
    """
    The update function updates a contact in the database.
    Args:
    contact_id (int): The id of the contact to update.
    body (ContactModel): The updated information for the specified user's
    contact. This is passed as JSON data in a request body, and must
    contain all fields that are not nullable in ContactModel, including
    first_name, last_name, email and phone number. It may also include
    birthday and additional data if desired by the user making this call.

    :param contact_id: int: Identify the contact that is being deleted
    :param body: ContactModel: Pass in the new contact information
    :param user: User: Get the user_id from the jwt token
    :param db: Session: Access the database
    :return: The updated contact
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        db.commit()
    return contact


async def remove(contact_id: int, user: User, db: Session):
    """
    The remove function removes a contact from the database.
    Args:
    contact_id (int): The id of the contact to be removed.
    user (User): The user who is removing the contact.
    db (Session): A connection to our database, used for querying and updating data.

    :param contact_id: int: Specify the id of the contact to be removed
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session to the function
    :return: The contact that is removed
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact
