from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import get_password_hash, authenticate_user, create_access_token
from app.dependencies import limiter
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Rate limiting для защиты от брутфорса
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Логин пользователя с возвратом JWT токена"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/search")
async def search_users(
    username: str,
    db: Session = Depends(get_db)
):
    # Сознательная уязвимость для демонстрации работы SAST
    query = f"SELECT * FROM users WHERE username = '{username}'"  # <-- SQL INJECTION
    result = db.execute(query)
    users = []
    for row in result:
        users.append({"id": row[0], "username": row[1], "email": row[2]})
    return users
