"""Dashboard API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.dashboard import Dashboard, DashboardWidget
from app.models.semantic import SemanticEntity
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardListResponse,
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    DashboardWidgetResponse,
    WidgetDataRequest,
    WidgetDataResponse,
)
from app.core.query.sql_generator import SQLGenerator
from app.core.query.executor import QueryExecutor


router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.post("", response_model=DashboardResponse, status_code=201)
async def create_dashboard(
    dashboard: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new dashboard with optional widgets."""
    # Create dashboard
    db_dashboard = Dashboard(
        owner_id=current_user.id,
        name=dashboard.name,
        description=dashboard.description,
        layout_config=dashboard.layout_config,
        global_filters=dashboard.global_filters,
        is_public=dashboard.is_public,
        is_favorite=dashboard.is_favorite,
        tags=dashboard.tags,
    )
    db.add(db_dashboard)
    await db.flush()  # Get dashboard ID

    # Create widgets
    for widget_data in dashboard.widgets:
        widget = DashboardWidget(
            dashboard_id=db_dashboard.id,
            title=widget_data.title,
            description=widget_data.description,
            query_config=widget_data.query_config,
            chart_config=widget_data.chart_config,
            grid_position=widget_data.grid_position.model_dump(),
            position_order=widget_data.position_order,
            refresh_interval=widget_data.refresh_interval,
        )
        db.add(widget)

    await db.commit()
    await db.refresh(db_dashboard)

    # Load with widgets
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.widgets))
        .where(Dashboard.id == db_dashboard.id)
    )
    return result.scalar_one()


@router.get("", response_model=DashboardListResponse)
async def list_dashboards(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, le=100),
    favorite_only: bool = QueryParam(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all dashboards for the current user."""
    query = select(Dashboard).where(Dashboard.owner_id == current_user.id)

    if favorite_only:
        query = query.where(Dashboard.is_favorite == True)

    query = query.order_by(Dashboard.updated_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query.options(selectinload(Dashboard.widgets)))
    dashboards = result.scalars().all()

    return DashboardListResponse(dashboards=list(dashboards), total=len(dashboards))


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific dashboard by ID."""
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.widgets))
        .where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return dashboard


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_update: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a dashboard."""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Update fields
    update_data = dashboard_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)

    await db.commit()
    await db.refresh(dashboard)

    # Load with widgets
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.widgets))
        .where(Dashboard.id == dashboard_id)
    )
    return result.scalar_one()


@router.delete("/{dashboard_id}", status_code=204)
async def delete_dashboard(
    dashboard_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a dashboard and all its widgets."""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    await db.delete(dashboard)
    await db.commit()


# Widget endpoints
@router.post("/{dashboard_id}/widgets", response_model=DashboardWidgetResponse, status_code=201)
async def add_widget(
    dashboard_id: UUID,
    widget: DashboardWidgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a widget to a dashboard."""
    # Verify dashboard exists and user owns it
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Create widget
    db_widget = DashboardWidget(
        dashboard_id=dashboard_id,
        title=widget.title,
        description=widget.description,
        query_config=widget.query_config,
        chart_config=widget.chart_config,
        grid_position=widget.grid_position.model_dump(),
        position_order=widget.position_order,
        refresh_interval=widget.refresh_interval,
    )
    db.add(db_widget)
    await db.commit()
    await db.refresh(db_widget)

    return db_widget


@router.put("/{dashboard_id}/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_widget(
    dashboard_id: UUID,
    widget_id: UUID,
    widget_update: DashboardWidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a widget."""
    # Verify dashboard exists and user owns it
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Get widget
    result = await db.execute(
        select(DashboardWidget).where(
            DashboardWidget.id == widget_id,
            DashboardWidget.dashboard_id == dashboard_id
        )
    )
    widget = result.scalar_one_or_none()

    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Update fields
    update_data = widget_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "grid_position" and value is not None:
            setattr(widget, field, value.model_dump())
        else:
            setattr(widget, field, value)

    await db.commit()
    await db.refresh(widget)

    return widget


@router.delete("/{dashboard_id}/widgets/{widget_id}", status_code=204)
async def delete_widget(
    dashboard_id: UUID,
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a widget from a dashboard."""
    # Verify dashboard exists and user owns it
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Delete widget
    await db.execute(
        delete(DashboardWidget).where(
            DashboardWidget.id == widget_id,
            DashboardWidget.dashboard_id == dashboard_id
        )
    )
    await db.commit()


@router.post("/{dashboard_id}/widgets/{widget_id}/data", response_model=WidgetDataResponse)
async def get_widget_data(
    dashboard_id: UUID,
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute query for a specific widget and return data.
    This is similar to query-builder/execute but uses widget's saved configuration.
    """
    import time

    # Get dashboard and widget
    result = await db.execute(
        select(Dashboard)
        .options(selectinload(Dashboard.widgets))
        .where(
            Dashboard.id == dashboard_id,
            Dashboard.owner_id == current_user.id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Get entity
    query_config = widget.query_config
    entity_id = query_config.get("entity_id")

    result = await db.execute(
        select(SemanticEntity)
        .options(
            selectinload(SemanticEntity.dimensions),
            selectinload(SemanticEntity.measures)
        )
        .where(
            SemanticEntity.id == entity_id,
            SemanticEntity.owner_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Generate SQL
    generator = SQLGenerator(entity)
    sql, params = generator.generate_sql(
        dimension_ids=query_config.get("dimension_ids", []),
        measure_ids=query_config.get("measure_ids", []),
        filters=query_config.get("filters", []),
        limit=query_config.get("limit", 1000)
    )

    # Execute query
    executor = QueryExecutor()
    data_source = await executor.find_data_source(
        entity.primary_table,
        current_user.id,
        db
    )

    start_time = time.time()
    df = await executor.execute_query(sql, params, data_source, db)
    execution_time_ms = int((time.time() - start_time) * 1000)

    return WidgetDataResponse(
        widget_id=widget_id,
        columns=df.columns.tolist(),
        data=df.to_dict('records'),
        row_count=len(df),
        generated_sql=sql,
        execution_time_ms=execution_time_ms
    )
