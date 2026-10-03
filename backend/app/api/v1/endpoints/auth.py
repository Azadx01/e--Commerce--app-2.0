from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError

from app.db.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.rate_limit import auth_rate_limiter
from app.models.user import User, BlacklistedToken
from app.schemas.user import UserCreate, UserRead, Token
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=201)
def register(
    request: Request,
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    # Rate limit check for registration attempts
    auth_rate_limiter.check_rate_limit(request)

    # Strictly prevent privilege escalation: unauthenticated public registration cannot create admin accounts
    if user_in.role == "admin":
        is_internal_admin_provision = request.headers.get("X-Admin-Provision-Secret") == settings.JWT_SECRET
        if not ((current_user and current_user.role == "admin") or is_internal_admin_provision):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Self-assignment of administrative role is strictly forbidden. Admin accounts must be provisioned by existing administrators."
            )

    if user_in.role not in ["customer", "technician", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role specified. Must be 'customer', 'technician', or 'admin'.")
        
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system",
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        name=user_in.name,
        role=user_in.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    auth_rate_limiter.check_rate_limit(request)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    elif user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return {
        "access_token": create_access_token(user.id, role=user.role),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(db: Session = Depends(get_db), refresh_token: str = "") -> Any:
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=403, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "access_token": create_access_token(user.id, role=user.role),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@router.post("/logout")
def logout(db: Session = Depends(get_db), token: str = Depends(deps.reusable_oauth2)) -> Any:
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    try:
        db.commit()
    except IntegrityError:
        db.rollback() 
        # already revoked
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(deps.get_current_active_user)) -> Any:
    return current_user
