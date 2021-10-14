import uvicorn
import re
import errors
from dataaccess import users as dataaccess_users
from fastapi import APIRouter, Depends, Path, Query
from fastapi.param_functions import Form
from passlib.context import CryptContext
from dataaccess.errors import RecordNotFoundError

router = APIRouter()

# Password context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_context.hash(password)

class PasswordRequestFormCustom:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        email: str = Form(...),
    ):
        self.username = username
        self.password = password
        self.email = email

class SignInRequestFormCustom:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...),
        
    ):
        self.email = email
        self.password = password
        

@router.post(
    "/api/signup",
    tags=["Authentication"],
    summary="Signup with login credentials",
    description="Signup to create an account",
    response_description="Account creation success or failure",
)
async def add_user(
        form_data: PasswordRequestFormCustom = Depends(),
):
    # Checking if username is not null or empty strings
    if(form_data.username!=None and form_data.username!='' and form_data.username not in [' '*i for i in range(10)]):
        pass
    else:
        raise errors.BadRequestError("Please Enter a Username")

    # Checking if password is not null or empty strings
    
    if(form_data.password!=None and form_data.password!='' and form_data.password not in [' '*i for i in range(10)]):
        pass
    else:
        raise errors.BadRequestError("Please Enter a Password")

    # Checking if password is valid

    rules = [lambda s: any(x.isupper() for x in s), # must have at least one uppercase
        lambda s: any(x.islower() for x in s),  # must have at least one lowercase
        lambda s: any(x.isdigit() for x in s),  # must have at least one number
        lambda s: len(s) >= 8,  # must be at least 8 characters
        lambda s: any((x in ['@', '_' ,'!', '#', '$', '%', '^', '&', '*', '?']) for x in s) # at least one special character                  
        ]
    
    if all(rule(form_data.password) for rule in rules) and form_data.username not in form_data.password:
        pass
    else:
        raise errors.BadRequestError("Please Enter a Valid Password")

    # Checking if email is not null or empty strings
    
    if(form_data.email!=None and form_data.email!='' and form_data.email not in [' '*i for i in range(10)]):
        pass
    else:
        raise errors.BadRequestError("Please Enter an Email")

    # Check if email is valid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if(re.fullmatch(regex,form_data.email)):
        pass
    else:
        raise errors.BadRequestError("Please Enter a Valid Email")

    # Check if username exists
    try:
        user = await dataaccess_users.get_by_name(form_data.username)
        raise errors.UserAlreadyExists("Username already exists")
    except RecordNotFoundError:
        pass

    try:
        user = await dataaccess_users.get_by_email(form_data.email)
        raise errors.UserAlreadyExists("Email already exists")
    except RecordNotFoundError:
        pass

    # Hash password
    hashed_password = get_password_hash(form_data.password)

    # Save user
    user = await dataaccess_users.create(
        username=form_data.username,
        email=form_data.email,
        hashed_password=hashed_password
    )

    return {"Success": True}

@router.post(
    "/api/sign_in",
    tags=["Authentication"],
    summary="Authenticate with login credentials",
    description="Authenticate with an username/password",
    response_description="Is login successful or not",
)
async def login(
    form_data: SignInRequestFormCustom = Depends(),
):
    try:
        # Get user
        user = await dataaccess_users.get_email(form_data.email)

        # Verify password
        if not verify_password(form_data.password, user["hashed_password"]):
            raise errors.IncorrectLoginError()

        return {"success": True}
    except:
        raise errors.AuthenticationError()


@router.post(
    "/api/clean",
    tags=["Cleanup"],
    summary="Delete all users",
    description="Delete all users from DB",
    response_description="Cleanup Successful",
)
async def clean():
    await dataaccess_users.delete_all()
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(router, host="0.0.0.0", port=3000)