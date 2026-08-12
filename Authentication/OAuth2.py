from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="a_very_secret_string")

oauth = OAuth()

GOOGLE_CLIENT_ID = "google_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "google_client_secret"

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@app.get("/login")
async def login(request: Request):
    redirect_url = request.url_for("auth_callback")

    return await oauth.google.authorize_redirect(request, redirect_url)


@app.get("/auth")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)

        user_info = token.get("userinfo")

        if user_info:
            email = user_info.get("email")
            name = user_info.get("name")

            return {
                "message": "OAuth Authentication Successful",
                "email": email,
                "name": name,
                "raw_token_data": token,
            }

    except Exception as e:
        return {"error": f"Authentication failed: {str(e)}"}
