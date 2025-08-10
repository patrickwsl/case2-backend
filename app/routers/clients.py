from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.models.client import Client
from app.repositories import client as client_repo
from app.core.security import require_role, get_current_user

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=list[ClientOut])
async def list_clients(
    skip: int = 0, 
    limit: int = 10, 
    search: str = Query(None), 
    status: str = Query("active"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Lista clientes com paginação e filtros opcionais.

    Args:
        skip (int): Quantidade de registros para pular.
        limit (int): Quantidade máxima de registros a retornar.
        search (str): Filtro por nome ou email.
        status (str): Filtro pelo status do cliente.
        db (AsyncSession): Sessão assíncrona do banco.
        user: Usuário autenticado (inject).

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    return await client_repo.get_clients(db, skip, limit, search, status)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """
    Obtém cliente pelo ID.

    Args:
        client_id (int): ID do cliente.
        db (AsyncSession): Sessão assíncrona do banco.
        user: Usuário autenticado (inject).

    Raises:
        HTTPException 404 se o cliente não existir.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db_client = await client_repo.get_client_by_id(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client


@router.post("/", response_model=ClientOut)
async def create_client(client_in: ClientCreate, db: AsyncSession = Depends(get_db), user=Depends(require_role("admin"))):
    """
    Cria um novo cliente (requer permissão admin).

    Args:
        client_in (ClientCreate): Dados do cliente.
        db (AsyncSession): Sessão assíncrona do banco.
        user: Usuário autenticado com role admin (inject).

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    client = Client(**client_in.model_dump())
    return await client_repo.create_client(db, client)


@router.put("/{client_id}", response_model=ClientOut)
async def update_client(client_id: int, client_in: ClientUpdate, db: AsyncSession = Depends(get_db), user=Depends(require_role("admin"))):
    """
    Atualiza um cliente existente pelo ID (requer permissão admin).

    Args:
        client_id (int): ID do cliente.
        client_in (ClientUpdate): Dados para atualização.
        db (AsyncSession): Sessão assíncrona do banco.
        user: Usuário autenticado com role admin (inject).

    Raises:
        HTTPException 404 se o cliente não existir.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db_client = await client_repo.get_client_by_id(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await client_repo.update_client(db, db_client, client_in.model_dump(exclude_unset=True))


@router.delete("/{client_id}")
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_role("admin"))):
    """
    Remove um cliente pelo ID (requer permissão admin).

    Args:
        client_id (int): ID do cliente.
        db (AsyncSession): Sessão assíncrona do banco.
        user: Usuário autenticado com role admin (inject).

    Raises:
        HTTPException 404 se o cliente não existir.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db_client = await client_repo.get_client_by_id(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    await client_repo.delete_client(db, db_client)
    return {"detail": "Client deleted"}
