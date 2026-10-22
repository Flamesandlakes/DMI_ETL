from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# NOTE: store this elsewhere, in a non-exposed location
user_db = {"testera": {
                        "username": "testera",
                        "role": "testing",
                        "hashed_password": "extremelyencryptedkodeord",
                        "disabled": "False"},
            "testerb": {
                        "username": "testerb",
                        "role": "testing",
                        "hashed_password": "extremelyencryptedkodeord2",
                        "disabled": "True"}
            }

app = FastAPI()

## Hash functions NOTE: should not be fully exposed in repo
# is used to avoid storing the passwords in plain text (a serious security issue otherwise)
def some_hash_function(password):
    return "extremelyencrypted" + password

def hash_password(password):
    return some_hash_function(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

## Data on each user
class User(BaseModel):
    username: str
    role: str | None = None
    disabled: bool | None = None

## ... and their password (in the user_db)
class UserInDB(User):
    hashed_password: str

def fake_decode_token(token): # NOTE: token != user password
    return User(
        username=token + "fakedecoded", role = "testing"
    )

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(user_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)], # depends on get_current_user, ie. authorized user
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = user_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
