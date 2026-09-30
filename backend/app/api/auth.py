import json
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token, get_current_user, verify_password
from backend.app.db.session import get_db
from backend.app.models.models import User
from backend.app.schemas.common import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """Login endpoint supporting both frontend JSON and Swagger OAuth2 form login.

    JSON (frontend): {"username": "engineer", "password": "Engineer@26120"}
    Form (Swagger OAuth2): username=engineer&password=Engineer%4026120
    """
    content_type = request.headers.get("content-type", "").lower()
    username = None
    password = None

    if "application/json" in content_type:
        try:
            payload = LoginRequest.model_validate(await request.json())
            username = payload.username
            password = payload.password
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=422, detail="Invalid JSON login payload")
    elif "application/x-www-form-urlencoded" in content_type:
        raw = (await request.body()).decode("utf-8")
        form = parse_qs(raw, keep_blank_values=True)
        username = form.get("username", [None])[0]
        password = form.get("password", [None])[0]
    else:
        raise HTTPException(
            status_code=415,
            detail="Use application/json or application/x-www-form-urlencoded",
        )

    if not username or not password:
        raise HTTPException(status_code=422, detail="Username and password are required")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return TokenResponse(access_token=create_access_token(user.id), role=user.role)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
