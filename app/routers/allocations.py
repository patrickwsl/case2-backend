from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories import allocations as allocation_repo
from app.schemas.allocation import AllocationCreateBySymbol, AllocationUpdate, AllocationResponse

router = APIRouter(prefix="/allocations", tags=["Allocations"])

@router.post("/", response_model=AllocationResponse)
async def create_allocation_endpoint(allocation: AllocationCreateBySymbol, db: AsyncSession = Depends(get_db)):
    """
    Cria uma nova alocação de um ativo para um cliente.

    Args:
        allocation (AllocationCreate): Dados para criação da alocação.
        db (AsyncSession): Sessão assíncrona do banco de dados.

    Returns:
        AllocationResponse: Dados da alocação criada.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    try:
        allocation_obj = await allocation_repo.create_allocation_by_symbol(db, allocation)
        return allocation_obj
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[AllocationResponse])
async def list_allocations(
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    client_id: Optional[int] = Query(None, description="Filter by client"),
    asset_id: Optional[int] = Query(None, description="Filter by asset"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    """
    Lista alocações, podendo filtrar pelo status ativo/inativo.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        is_active (Optional[bool]): Filtra por alocações ativas (True), inativas (False) ou todas (None).
        client_id: Optional[int] = Query(None, description="Filter by client")
        asset_id: Optional[int] = Query(None, description="Filter by asset")
        page: int = Query(1, ge=1)
        limit: int = Query(10, ge=1)

    Returns:
        List[AllocationResponse]: Lista de alocações conforme filtro.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return await allocation_repo.get_all_allocations(
        db, is_active=is_active, client_id=client_id, asset_id=asset_id, page=page, limit=limit
    )

@router.get("/{allocation_id}", response_model=AllocationResponse)
async def get_allocation(allocation_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna detalhes de uma alocação específica pelo seu ID.

    Args:
        allocation_id (int): ID da alocação.
        db (AsyncSession): Sessão assíncrona do banco.

    Raises:
        HTTPException: 404 se a alocação não for encontrada.

    Returns:
        AllocationResponse: Dados da alocação solicitada.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    db_allocation = await allocation_repo.get_allocation_by_id(db, allocation_id)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.put("/{allocation_id}", response_model=AllocationResponse)
async def update_allocation_endpoint(allocation_id: int, allocation: AllocationUpdate, db: AsyncSession = Depends(get_db)):
    """
    Atualiza dados de uma alocação existente.

    Args:
        allocation_id (int): ID da alocação a ser atualizada.
        allocation (AllocationUpdate): Dados para atualização.
        db (AsyncSession): Sessão assíncrona do banco.

    Raises:
        HTTPException: 404 se a alocação não for encontrada.

    Returns:
        AllocationResponse: Dados da alocação atualizada.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    db_allocation = await allocation_repo.update_allocation(db, allocation_id, allocation)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.delete("/{allocation_id}")
async def delete_allocation_endpoint(allocation_id: int, db: AsyncSession = Depends(get_db)):
    """
    Marca uma alocação como inativa (soft delete).

    Args:
        allocation_id (int): ID da alocação a ser deletada.
        db (AsyncSession): Sessão assíncrona do banco.

    Returns:
        dict: Mensagem de sucesso ou erro.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return await allocation_repo.delete_allocation(db, allocation_id)