from dataaccess.errors import RecordNotFoundError
from typing import Any, Dict, List

Database = []

async def get_by_name(username: str) -> Dict[str, Any]:
    """
    Retrieve one row based by its name. Return object is a dict. 
    Raises if the record was not found.
    """

    username = username.lower()

    for user in Database:
        if(user["username"] == username):
            return user

    raise RecordNotFoundError(f"Could not find row with username '{username}'")



async def get_by_email(email: str) -> Dict[str, Any]:
    """
    Retrieve one row based by its email. Return object is a dict. 
    Raises if the record was not found.
    """

    email = email.lower()

    for user in Database:
        if(user["email"] == email):
            return user

    raise RecordNotFoundError(f"Could not find row with email '{email}'")

async def create(*,    
                 username: str,
                 email: str = None,
                 hashed_password: str = None,
                 id: int = None) -> Dict[str, Any]:
    """
    Create a new row. Returns the created record as a dict.
    """

    username = username.lower()
    user = {"username":username, "email":email, "hashed_password":hashed_password}
    Database.append(user)
    return user

async def delete_all():

    Database.clear()

