import asyncio
import uuid
from sqlalchemy import select, literal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.edge import LineageEdge
from app.clients.registry_client import RegistryClient
from app.exceptions import (
    EdgeNotFound,
    EdgeAlreadyExists,
    CycleDetected,
    DatasetNotFoundInRegistry,
    ServiceUnavailableError,
)
from app.schemas.edge import EdgeCreate


class LineageCRUD:
    """
    Combined CRUD for lineage edges and graph traversal.
    Replaces both EdgeCRUD and DatasetCRUD.
    All graph queries return raw UUIDs (no local Dataset table).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_edge(
        self, edge_in: EdgeCreate, registry_client: RegistryClient
    ) -> LineageEdge:
        """
        Create a lineage edge after verifying both dataset IDs
        exist in Registry and the edge would not create a cycle.
        """
        # 1. Verify both datasets exist in Registry (parallel)
        try:
            upstream_ds, downstream_ds = await asyncio.gather(
                registry_client.get_dataset(str(edge_in.upstream_id)),
                registry_client.get_dataset(str(edge_in.downstream_id)),
            )
        except Exception as e:
            raise ServiceUnavailableError(
                service_name="Registry",
                detail=str(e),
            )

        if upstream_ds is None:
            raise DatasetNotFoundInRegistry(dataset_id=str(edge_in.upstream_id))
        if downstream_ds is None:
            raise DatasetNotFoundInRegistry(dataset_id=str(edge_in.downstream_id))

        # 2. Cycle detection: check if upstream_id is reachable from downstream_id
        impacted_ids = await self.get_impact_analysis(edge_in.downstream_id)
        if edge_in.upstream_id in impacted_ids:
            raise CycleDetected(
                upstream_id=str(edge_in.upstream_id),
                downstream_id=str(edge_in.downstream_id),
            )

        # 3. Create the edge
        edge = LineageEdge(
            upstream_id=edge_in.upstream_id,
            downstream_id=edge_in.downstream_id,
        )
        self.db.add(edge)
        try:
            await self.db.commit()
            await self.db.refresh(edge)
        except IntegrityError:
            await self.db.rollback()
            raise EdgeAlreadyExists(
                upstream_id=str(edge_in.upstream_id),
                downstream_id=str(edge_in.downstream_id),
            )

        return edge

    async def delete_edge(
        self, upstream_id: uuid.UUID, downstream_id: uuid.UUID
    ) -> LineageEdge:
        edge = await self.db.get(LineageEdge, (upstream_id, downstream_id))
        if not edge:
            raise EdgeNotFound(
                upstream_id=str(upstream_id),
                downstream_id=str(downstream_id),
            )
        await self.db.delete(edge)
        await self.db.commit()
        return edge

    async def get_impact_analysis(self, dataset_id: uuid.UUID) -> list[uuid.UUID]:
        """
        Downstream impact analysis via recursive CTE.
        Returns list of dataset UUIDs that are downstream of the given dataset.
        """
        # Base case: direct downstream
        base_query = select(LineageEdge.downstream_id).where(
            LineageEdge.upstream_id == dataset_id
        )

        cte = base_query.cte(name="impact_cte", recursive=True)

        edge_alias = aliased(LineageEdge)

        # Recursive step
        recursive_step = select(edge_alias.downstream_id).join(
            cte, edge_alias.upstream_id == cte.c.downstream_id
        )

        cte = cte.union_all(recursive_step)

        # Final query — return distinct UUIDs
        final_query = select(cte.c.downstream_id).distinct()

        result = await self.db.execute(final_query)
        return list(result.scalars().all())

    async def get_impact_with_depth(
        self, dataset_id: uuid.UUID
    ) -> list[tuple[uuid.UUID, int]]:
        """
        Downstream impact with hop depth tracking.
        Returns list of (dataset_uuid, depth) tuples.
        """
        base_query = select(
            LineageEdge.downstream_id,
            literal(1).label("depth"),
        ).where(LineageEdge.upstream_id == dataset_id)

        cte = base_query.cte(name="impact_depth_cte", recursive=True)

        edge_alias = aliased(LineageEdge)

        recursive_step = select(
            edge_alias.downstream_id,
            (cte.c.depth + 1).label("depth"),
        ).join(cte, edge_alias.upstream_id == cte.c.downstream_id)

        cte = cte.union_all(recursive_step)

        final_query = (
            select(cte.c.downstream_id, cte.c.depth)
            .distinct()
            .order_by(cte.c.depth)
        )

        result = await self.db.execute(final_query)
        return result.all()

    async def get_root_cause_analysis(
        self, dataset_id: uuid.UUID
    ) -> list[uuid.UUID]:
        """
        Upstream root cause analysis via recursive CTE.
        Returns list of dataset UUIDs that are upstream of the given dataset.
        """
        base_query = select(LineageEdge.upstream_id).where(
            LineageEdge.downstream_id == dataset_id
        )

        cte = base_query.cte(name="cause_cte", recursive=True)

        edge_alias = aliased(LineageEdge)

        recursive_step = select(edge_alias.upstream_id).join(
            cte, edge_alias.downstream_id == cte.c.upstream_id
        )

        cte = cte.union_all(recursive_step)

        final_query = select(cte.c.upstream_id).distinct()

        result = await self.db.execute(final_query)
        return list(result.scalars().all())
