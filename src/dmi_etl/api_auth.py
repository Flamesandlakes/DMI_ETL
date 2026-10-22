from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
### STORE ELSEWHERE: FROM HERE ... ####
SECRET_KEY = "MwVJAU6Yzcn366jCCJlKQX1IYuMqw+jIfHsYpvzw1Qk="

# NOTE: store this elsewhere, in a non-exposed location
users_db = {"tester": {
                        "username": "tester",
                        "role": "testing",
                        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$PC3/ehfXJ7jLdKmi5+Xy6A$tCR1gVRM/jKOR/V/H79ythjvbHRD9wdnT1AOWrUnniI",
                        "disabled": "False"},
            "testerb": {
                        "username": "testerb",
                        "role": "testing",
                        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$kKJ/uJJ/tpeRne4s9Ovt7Q$V1/9GlCApFOIjd7tVezYN0/P3nYb+JG0eCljKWktPTk",
                        "disabled": "True"},
            }
### ... TO HERE ####


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

# define app (later given methods)
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# verify that plain matched stored hashed version
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)

## Token class
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

## User class
class User(BaseModel):
    username: str
    role: str | None = None
    disabled: bool | None = None

# ... and their password (in the user_db)
class UserInDB(User):
    hashed_password: str


# from database, retrieve data on user (in db)
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}


if __name__ == "__main__":
    example = "kodeordb"
    hashed_example = get_password_hash(example)
    print(hashed_example)
    