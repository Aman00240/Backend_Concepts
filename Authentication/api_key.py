import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

app = FastAPI()

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

VALID_API_KEYS = {
    "sk_live_1234567890abcdef": "aman_1",
    "sk_test_0987654321fedcba": "aman_2",
}


def verify_api_key(api_key: str = Depends(api_key_header)):
    client_name = VALID_API_KEYS.get(api_key)

    if not client_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return {"client": client_name}


@app.post("/generate-key")
def generate_key(project_name: str):

    new_key = f"sk_live_{secrets.token_hex(16)}"

    VALID_API_KEYS[new_key] = project_name

    return {"message": "Key Generated", "Key": new_key}


@app.get("/data")
def get_data(client_info: dict = Depends(verify_api_key)):
    return {
        "message": "Access granted",
        "client": client_info["client"],
        "data": "This is server-to-server data",
    }
