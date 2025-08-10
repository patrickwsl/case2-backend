from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.repositories.user import create_user, get_user_by_username
from app.core.security import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra um novo usuário.

    Args:
        user (UserCreate): Dados do usuário para criação.
        db (AsyncSession): Sessão assíncrona do banco.

    Raises:
        HTTPException 400 se username já existir.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = await create_user(db, user, hashed_password)
    return new_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Realiza login e retorna token JWT.

    Args:
        form_data (OAuth2PasswordRequestForm): Dados do formulário de login.
        db (AsyncSession): Sessão assíncrona do banco.

    Raises:
        HTTPException 401 se usuário/senha inválidos.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}
