from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date

from app.models.allocation import Allocation
from app.models.asset import Asset
from app.schemas.allocation import AllocationCreate, AllocationUpdate
from app.repositories.assets_repository import get_asset_price

async def create_allocation(db: AsyncSession, allocation: AllocationCreate):
    """
    Cria uma nova alocação de ativo para um cliente.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        allocation (AllocationCreate): Dados da alocação a ser criada.

    Returns:
        Allocation: Objeto Allocation criado.

    Raises:
        ValueError: Se o ativo não for encontrado.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    result = await db.execute(select(Asset).filter(Asset.id == allocation.asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise ValueError("Asset not found")

    current_price = await get_asset_price(asset.ticker)

    db_allocation = Allocation(
        client_id=allocation.client_id,
        asset_id=allocation.asset_id,
        quantity=allocation.quantity,
        buy_price=current_price if allocation.buy_price is None else allocation.buy_price,
        buy_date=allocation.buy_date or date.today()
    )
    db.add(db_allocation)
    await db.commit()
    await db.refresh(db_allocation)
    return db_allocation

async def get_all_allocations(db: AsyncSession, is_active: Optional[bool] = None):
    """
    Obtém lista de alocações, opcionalmente filtrando por status ativo/inativo.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        is_active (Optional[bool]): Filtra por alocações ativas (True), inativas (False) ou todas (None).

    Returns:
        list: Lista de objetos Allocation.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    query = select(Allocation)
    if is_active is not None:
        query = query.where(Allocation.is_active == is_active)
    result = await db.execute(query)
    return result.scalars().all()

async def get_allocation_by_id(db: AsyncSession, allocation_id: int):
    """
    Obtém uma alocação pelo seu ID.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        allocation_id (int): ID da alocação.

    Returns:
        Allocation | None: Objeto Allocation ou None se não encontrado.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    result = await db.execute(select(Allocation).filter(Allocation.id == allocation_id))
    return result.scalar_one_or_none()

async def update_allocation(db: AsyncSession, allocation_id: int, allocation: AllocationUpdate):
    """
    Atualiza os dados de uma alocação existente.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        allocation_id (int): ID da alocação a atualizar.
        allocation (AllocationUpdate): Dados para atualização.

    Returns:
        Allocation | None: Alocação atualizada ou None se não encontrada.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    db_allocation = await get_allocation_by_id(db, allocation_id)
    if not db_allocation:
        return None

    for field, value in allocation.dict(exclude_unset=True).items():
        setattr(db_allocation, field, value)

    await db.commit()
    await db.refresh(db_allocation)
    return db_allocation

async def delete_allocation(db: AsyncSession, allocation_id: int):
    """
    Marca uma alocação como inativa (soft delete).

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        allocation_id (int): ID da alocação a ser inativada.

    Returns:
        dict: Mensagem de sucesso ou erro.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    db_allocation = await get_allocation_by_id(db, allocation_id)
    if not db_allocation:
        return {"error": "Allocation not found"}

    db_allocation.is_active = False
    db.add(db_allocation)
    await db.commit()
    return {"message": "Allocation marked as inactive successfully"}

async def get_by_client(db: AsyncSession, client_id: int):
    """
    Retorna todas as alocações de um cliente específico.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        client_id (int): ID do cliente.

    Returns:
        list[Allocation]: Lista de alocações.
    """
    result = await db.execute(
        select(Allocation)
        .options(selectinload(Allocation.asset))
        .where(Allocation.client_id == client_id)
    )
    return result.scalars().all()