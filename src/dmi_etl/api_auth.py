from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from pydantic import BaseModel, ValidationError

from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
### STORE ELSEWHERE: FROM HERE ... ####
SECRET_KEY = "MwVJAU6Yzcn366jCCJlKQX1IYuMqw+jIfHsYpvzw1Qk="

# NOTE: store this elsewhere, in a non-exposed location
users_db = {"tester": {
                        "username": "tester",
                        "role": "testing",
                        "access": ["me", 
                                  "parameters_admin",
                                  "stations_admin",
                                  "readings_admin"],
                        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$PC3/ehfXJ7jLdKmi5+Xy6A$tCR1gVRM/jKOR/V/H79ythjvbHRD9wdnT1AOWrUnniI",
                        "disabled": "False"},
            "testerb": {
                        "username": "testerb",
                        "role": "anon",
                        "access": ["me",
                                  "parameters_read",
                                  "stations_read",
                                  "readings_read"],
                        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$kKJ/uJJ/tpeRne4s9Ovt7Q$V1/9GlCApFOIjd7tVezYN0/P3nYb+JG0eCljKWktPTk",
                        "disabled": "False"},
            }
### ... TO HERE ####


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

# define app (later given methods)
app = APIRouter() #FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",
                                    #  scopes = {"me": "Read information about the current user.",
                                    #            "readings_read": "Read climate readings.",
                                    #            "readings_admin": "Read, write, update or delete climate readings.",
                                    #            "stations_read": "Read station metadata.",
                                    #            "stations_admin": "Read, write, update or delete station metadata.",
                                    #            "parameters_read": "Read parameter metadata.",
                                    #            "parameters_admin": "Read, write, update or delete parameter metadata."}
                                     )

# verify that plain matched stored hashed version
def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return password_hash.hash(password)

## Token class
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    access: list[str] = []

## User class
class User(BaseModel):
    username: str
    role: str | None = None
    disabled: bool | None = None

# ... and their password (in the user_db)
class UserInDB(User):
    hashed_password: str
    access: list[str] = []


# from database, retrieve data on user (in db)
def get_user(db, username: str) -> UserInDB:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(users_db, username: str, password: str) -> dict | bool:
    user = get_user(users_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

##
# from typing import Callable


# def require_role(required_role: str) -> Callable:
#     def role_checker(user: dict = Depends(authenticate_user)) -> dict:
#         if user["role"] != required_role:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Insufficient permissions",
#             )
#         return user
#     return role_checker


def check_authorization(client, any_of_perm:list | str):
    '''
    Check whether client fulfill any of the prerequisite access requirements.
    '''
    if isinstance(any_of_perm, str):
        any_of_perm = [any_of_perm]
        
    eval = []
    for perm in any_of_perm:
        if perm in client.access:
            eval.append(True)
    if any(eval):
        return True
    else:
        raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions",
                    )

## create a temporary access token. Used to verify user without needing repeated logins
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) # if no expiration is specified, set expiration to 15 minutes
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # NOTE: jwt = JSON Web Token
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        scope: str = payload.get("scope", "")
        token_scopes = scope.split(" ")
        token_data = TokenData(scopes=token_scopes,username=username)
        
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)], # depends on get_current_user, ie. authorized user
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# using token to access api
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])]):
    return current_user

@app.get("/token/me", response_model=TokenData)
async def read_token(current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])], token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
    