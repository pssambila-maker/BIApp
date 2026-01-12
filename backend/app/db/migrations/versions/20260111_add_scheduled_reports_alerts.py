"""Add scheduled reports, alerts, and email configuration tables

Revision ID: add_reports_alerts_001
Revises: add_dashboard_001
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_reports_alerts_001'
down_revision = 'add_dashboard_001'
depends_on = None


def upgrade() -> None:
    # Create email_configurations table
    op.create_table('email_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('smtp_host', sa.String(length=255), nullable=False),
        sa.Column('smtp_port', sa.Integer(), nullable=False),
        sa.Column('use_tls', sa.Boolean(), nullable=False),
        sa.Column('use_ssl', sa.Boolean(), nullable=False),
        sa.Column('smtp_username', sa.String(length=255), nullable=False),
        sa.Column('smtp_password_encrypted', sa.String(length=512), nullable=False),
        sa.Column('from_email', sa.String(length=255), nullable=False),
        sa.Column('from_name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_email_configurations_owner_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_email_configurations')),
        sa.UniqueConstraint('owner_id', name='uix_email_config_owner')
    )
    op.create_index(op.f('ix_email_configurations_owner_id'), 'email_configurations', ['owner_id'], unique=False)

    # Create scheduled_reports table
    op.create_table('scheduled_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('saved_query_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('schedule_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('recipients', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('formats', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('email_subject', sa.String(length=255), nullable=True),
        sa.Column('email_body', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], name=op.f('fk_scheduled_reports_dashboard_id_dashboards'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_scheduled_reports_owner_id_users'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['saved_query_id'], ['saved_queries.id'], name=op.f('fk_scheduled_reports_saved_query_id_saved_queries'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_scheduled_reports'))
    )
    op.create_index(op.f('ix_scheduled_reports_dashboard_id'), 'scheduled_reports', ['dashboard_id'], unique=False)
    op.create_index(op.f('ix_scheduled_reports_next_run_at'), 'scheduled_reports', ['next_run_at'], unique=False)
    op.create_index(op.f('ix_scheduled_reports_owner_id'), 'scheduled_reports', ['owner_id'], unique=False)
    op.create_index(op.f('ix_scheduled_reports_saved_query_id'), 'scheduled_reports', ['saved_query_id'], unique=False)

    # Create report_executions table
    op.create_table('report_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('scheduled_report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('triggered_by', sa.String(length=50), nullable=False),
        sa.Column('generated_files', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sent_to', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['scheduled_report_id'], ['scheduled_reports.id'], name=op.f('fk_report_executions_scheduled_report_id_scheduled_reports'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_report_executions'))
    )
    op.create_index(op.f('ix_report_executions_created_at'), 'report_executions', ['created_at'], unique=False)
    op.create_index(op.f('ix_report_executions_scheduled_report_id'), 'report_executions', ['scheduled_report_id'], unique=False)

    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('saved_query_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('condition_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('check_frequency', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('recipients', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('notification_message', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_alerts_owner_id_users'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['saved_query_id'], ['saved_queries.id'], name=op.f('fk_alerts_saved_query_id_saved_queries'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_alerts'))
    )
    op.create_index(op.f('ix_alerts_owner_id'), 'alerts', ['owner_id'], unique=False)
    op.create_index(op.f('ix_alerts_saved_query_id'), 'alerts', ['saved_query_id'], unique=False)

    # Create alert_executions table
    op.create_table('alert_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('condition_met', sa.Boolean(), nullable=False),
        sa.Column('condition_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=False),
        sa.Column('notified_recipients', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], name=op.f('fk_alert_executions_alert_id_alerts'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_alert_executions'))
    )
    op.create_index(op.f('ix_alert_executions_alert_id'), 'alert_executions', ['alert_id'], unique=False)
    op.create_index(op.f('ix_alert_executions_created_at'), 'alert_executions', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alert_executions_created_at'), table_name='alert_executions')
    op.drop_index(op.f('ix_alert_executions_alert_id'), table_name='alert_executions')
    op.drop_table('alert_executions')

    op.drop_index(op.f('ix_alerts_saved_query_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_owner_id'), table_name='alerts')
    op.drop_table('alerts')

    op.drop_index(op.f('ix_report_executions_scheduled_report_id'), table_name='report_executions')
    op.drop_index(op.f('ix_report_executions_created_at'), table_name='report_executions')
    op.drop_table('report_executions')

    op.drop_index(op.f('ix_scheduled_reports_saved_query_id'), table_name='scheduled_reports')
    op.drop_index(op.f('ix_scheduled_reports_owner_id'), table_name='scheduled_reports')
    op.drop_index(op.f('ix_scheduled_reports_next_run_at'), table_name='scheduled_reports')
    op.drop_index(op.f('ix_scheduled_reports_dashboard_id'), table_name='scheduled_reports')
    op.drop_table('scheduled_reports')

    op.drop_index(op.f('ix_email_configurations_owner_id'), table_name='email_configurations')
    op.drop_table('email_configurations')
