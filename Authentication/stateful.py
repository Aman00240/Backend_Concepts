import uuid

import redis
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

USER_DB = {"aman": "pass123"}

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="not authenticated")

    username = redis_client.get(session_id)

    if not username:
        raise HTTPException(status_code=401, detail="Session Expired or invalid")

    return {"username": username}


@app.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    password = USER_DB.get(form_data.username)

    if not password or password != form_data.password:
        raise HTTPException(status_code=400, detail="incorrect credentials")

    session_id = str(uuid.uuid4())

    redis_client.setex(session_id, 3600, form_data.username)

    response.set_cookie(
        key="session_id", value=session_id, httponly=True, samesite="lax", max_age=3600
    )

    return {"message": "Logged In"}


@app.get("/get_data")
def get_data(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Authentication successful",
        "user": current_user["username"],
        "data": "This is restricted information",
    }


@app.post("/logout")
def logout(response: Response, request: Request):
    session_id = request.cookies.get("session_id")

    if session_id:
        redis_client.delete(session_id)

    response.delete_cookie("session_id")

    return {"message": "logged out succesfully"}
