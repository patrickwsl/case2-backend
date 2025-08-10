from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.repositories.user import get_user_by_username
from app.database import get_db
from app.models.user import UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash armazenado.

    Args:
        plain_password (str): Senha em texto plano fornecida pelo usuário.
        hashed_password (str): Senha hasheada armazenada no banco.

    Returns:
        bool: True se a senha bate, False caso contrário.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha fornecida.

    Args:
        password (str): Senha em texto plano.

    Returns:
        str: Senha hasheada para armazenamento seguro.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Autentica o usuário verificando se o username existe e se a senha está correta.

    Args:
        db (AsyncSession): Sessão assíncrona do banco de dados.
        username (str): Nome de usuário fornecido para login.
        password (str): Senha em texto plano fornecida para autenticação.

    Returns:
        User | None: Retorna o objeto User se autenticado com sucesso, ou None se falhar.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Cria um token JWT com dados codificados e tempo de expiração.

    Args:
        data (dict): Dados para incluir no payload do token (ex: sub, role).
        expires_delta (timedelta | None): Tempo opcional para expiração do token.

    Returns:
        str: Token JWT codificado.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Extrai o usuário atual a partir do token JWT.

    Args:
        token (str): Token JWT passado via cabeçalho Authorization Bearer.
        db (AsyncSession): Sessão assíncrona do banco para buscar o usuário.

    Raises:
        HTTPException 401: Se token for inválido ou usuário não encontrado.

    Returns:
        User: Objeto do usuário autenticado.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


def require_role(role: UserRole):
    """
    Dependency para garantir que o usuário atual possua a role especificada.

    Args:
        role (UserRole): Role necessária para acessar o recurso.

    Raises:
        HTTPException 403: Se o usuário não possuir permissão suficiente.

    Returns:
        Callable: Dependency function para ser usada com Depends() no FastAPI.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    async def role_checker(user=Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user
    return role_checker
