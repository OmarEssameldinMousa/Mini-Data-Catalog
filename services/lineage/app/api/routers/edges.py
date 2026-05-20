import asyncio
import uuid

from fastapi import APIRouter, Depends, Request, status
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.settings import get_settings
from app.crud.lineage import LineageCRUD
from app.clients.registry_client import RegistryClient
from app.schemas.edge import EdgeCreate, EdgeResponse
from app.schemas.dataset import DatasetDepthResponse, LineageGraphResponse

router = APIRouter(
    prefix="/lineage",
    tags=["lineage"],
)


def _get_registry_client(request: Request) -> RegistryClient:
    settings = get_settings()
    return RegistryClient(
        http_client=request.app.state.http_client,
        base_url=settings.registry_url,
    )


# ── Edge endpoints ──

@router.post("/edges", status_code=status.HTTP_201_CREATED, response_model=EdgeResponse)
async def create_edge(
    request: Request,
    edge_data: EdgeCreate = Body(...),
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    registry_client = _get_registry_client(request)
    edge = await crud.create_edge(edge_data, registry_client=registry_client)
    return edge


@router.delete("/edges/{upstream_id}/{downstream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    upstream_id: uuid.UUID,
    downstream_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    await crud.delete_edge(upstream_id, downstream_id)


# ── Lineage query endpoints (moved from datasets router) ──

@router.get("/datasets/{dataset_id}/impact", response_model=list[uuid.UUID])
async def get_impact(
    dataset_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    impacted_ids = await crud.get_impact_analysis(dataset_id=dataset_id)
    return impacted_ids


@router.get("/datasets/{dataset_id}/impact-depth", response_model=list[DatasetDepthResponse])
async def get_impact_with_depth(
    dataset_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    results = await crud.get_impact_with_depth(dataset_id=dataset_id)
    return [
        DatasetDepthResponse(dataset_id=ds_id, depth=depth)
        for ds_id, depth in results
    ]


@router.get("/datasets/{dataset_id}/root-cause", response_model=list[uuid.UUID])
async def get_root_cause(
    dataset_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    upstream_ids = await crud.get_root_cause_analysis(dataset_id=dataset_id)
    return upstream_ids


@router.get("/datasets/{dataset_id}/lineage", response_model=LineageGraphResponse)
async def get_full_lineage(
    dataset_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db),
):
    crud = LineageCRUD(db_session)
    upstream_ids, downstream_ids = await asyncio.gather(
        crud.get_root_cause_analysis(dataset_id=dataset_id),
        crud.get_impact_analysis(dataset_id=dataset_id),
    )
    return LineageGraphResponse(
        upstream=upstream_ids,
        downstream=downstream_ids,
    )