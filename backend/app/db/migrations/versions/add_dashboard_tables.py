"""Add dashboard and dashboard_widget tables

Revision ID: add_dashboard_001
Revises:
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_dashboard_001'
down_revision = '32df6e9fa0b6'
depends_on = None


def upgrade() -> None:
    # Create dashboards table
    op.create_table('dashboards',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('layout_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('global_filters', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('is_favorite', sa.Boolean(), nullable=True),
    sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_dashboards_owner_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_dashboards'))
    )

    # Create dashboard_widgets table
    op.create_table('dashboard_widgets',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('query_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('chart_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('grid_position', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('position_order', sa.Integer(), nullable=True),
    sa.Column('refresh_interval', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], name=op.f('fk_dashboard_widgets_dashboard_id_dashboards'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_dashboard_widgets'))
    )


def downgrade() -> None:
    op.drop_table('dashboard_widgets')
    op.drop_table('dashboards')
