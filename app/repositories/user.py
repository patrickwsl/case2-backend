from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate

async def get_user_by_username(db: AsyncSession, username: str):
    """
    Busca um usuário pelo nome de usuário.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        username (str): Nome do usuário.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Busca um usuário pelo email.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        email (str): Email do usuário.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate, hashed_password: str):
    """
    Cria um novo usuário com senha hasheada.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        user (UserCreate): Dados do usuário para criar.
        hashed_password (str): Senha hasheada para salvar.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
