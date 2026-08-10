import time

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

SECRET_KEY = "ca7fa36d"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

FAKEDB = {"aman": "pass123"}


class UserCreate(BaseModel):
    username: str
    password: str


def create_jwt_token(data: dict):
    payload = data.copy()

    expire = time.time() + 3600
    payload.update({"exp": expire})

    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

    return token


def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has Expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )


@app.post("/signup")
def signup(user: UserCreate):
    if user.username in FAKEDB:
        raise HTTPException(status_code=400, detail="Username already registered")

    FAKEDB[user.username] = user.password

    return {"message": "User Created"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    password = FAKEDB.get(form_data.username)

    if not password or password != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    token = create_jwt_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/data")
def get_data(current_user: dict = Depends(verify_jwt_token)):
    username = current_user.get("sub")

    return {
        "message": "Authentication successful",
        "user": username,
        "data": "This is restricted information.",
    }
