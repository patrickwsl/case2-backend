from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.models.client import Client

async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 10, search: str = None, status: str = "active"):
    """
    Busca lista de clientes com filtros opcionais e paginação.
    Por padrão retorna somente clientes com status 'active'.

    Args:
        db (AsyncSession): Sessão assíncrona do banco de dados.
        skip (int): Quantidade de registros a pular.
        limit (int): Quantidade máxima de registros a retornar.
        search (str): Filtro para nome ou email (contendo).
        status (str): Filtro pelo status do cliente (default 'active').

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    query = select(Client)
    if search:
        query = query.filter(or_(Client.name.ilike(f"%{search}%"), Client.email.ilike(f"%{search}%")))
    if status:
        query = query.filter(Client.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def get_client_by_id(db: AsyncSession, client_id: int):
    """
    Busca um cliente pelo ID.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        client_id (int): ID do cliente.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    result = await db.execute(select(Client).filter(Client.id == client_id))
    return result.scalar_one_or_none()

async def create_client(db: AsyncSession, client: Client):
    """
    Cria um novo cliente.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        client (Client): Instância do cliente para criar.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

async def update_client(db: AsyncSession, db_client: Client, updates: dict):
    """
    Atualiza os dados de um cliente existente.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        db_client (Client): Cliente a ser atualizado.
        updates (dict): Dicionário com os campos a atualizar.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    for key, value in updates.items():
        setattr(db_client, key, value)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def delete_client(db: AsyncSession, db_client: Client):
    """
    Inativa um cliente, atualizando seu status para 'inactive'.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        db_client (Client): Cliente a ser inativado.

    Author: Patrick Lima (patrickwsl)

    Date: 10th August 2025
    """
    db_client.status = "inactive"
    await db.commit()
    await db.refresh(db_client)
    return db_client
