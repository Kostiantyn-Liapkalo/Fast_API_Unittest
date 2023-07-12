from typing import List

from fastapi import Request, Depends, HTTPException, status

from src.database.models import User, Role
from src.services.auth import auth_service


class RolesAccess:
    def __init__(self, allowed_roles: List[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and takes in any arguments that are required to do so.
        In this case, we're taking in a list of allowed roles.

        :param self: Represent the instance of the class
        :param allowed_roles: List[Role]: Define the allowed roles for a user
        :return: A new instance of the class
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is a decorator that allows us to use the class as a function.
        It takes in the request and current_user, which are passed by FastAPI automatically.
        The __call__ function then checks if the user's role is allowed to access this endpoint.

        :param self: Refer to the class instance itself
        :param request: Request: Get the request object
        :param current_user: User: Get the current user from the auth_service
        :return: A function that takes in a request and current_user
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")