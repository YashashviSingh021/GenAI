import jwt
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

JWT_SECRET_KEY = "c6ecd2b8-4109-4cbe-aff3-fadb502ff77e"
JWT_ALOGO = "HS256"
JWT_ISSUER = "http://localhost:8001"
JWT_EXPIRE_HOURS = 1
JWT_AUDIENCE = "my-mcp-server"

app = FastAPI(
    title="JWT Token Generator",

)

class TokenRequest(BaseModel):
    user_id: str
    email: str
    password:str

class TokenResponse(BaseModel):
    access_token: str
    expires_in: int


@app.post("/token", response_model=TokenResponse)
def generate_jwt_token(req: TokenRequest) :
    timenow = datetime.now()
    expiration_time = timenow + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": req.user_id,
        "email": req.email,
        "exp": expiration_time,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": timenow
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALOGO)
    return TokenResponse(access_token=token, expires_in=JWT_EXPIRE_HOURS)

@app.get("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)