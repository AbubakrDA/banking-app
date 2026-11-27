"""006_tickets_and_feedback

Revision ID: 006_tickets
Revises: 005_memory
Create Date: 2026-11-24 14:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006_tickets'
down_revision: Union[str, None] = '005_memory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('ticket_number', sa.String(length=64), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('priority', sa.String(length=32), server_default='medium', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='new', nullable=False),
        sa.Column('assigned_user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sla_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_escalated', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('escalation_reason', sa.String(length=255), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tickets_tenant_id', 'tickets', ['tenant_id'])
    op.create_index('ix_tickets_customer_id', 'tickets', ['customer_id'])
    op.create_index('ix_tickets_ticket_number', 'tickets', ['ticket_number'])
    op.create_index('ix_tickets_status', 'tickets', ['status'])

    # 2. Ticket Notes table
    op.create_table(
        'ticket_notes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('author_name', sa.String(length=128), server_default='System', nullable=False),
        sa.Column('note_type', sa.String(length=32), server_default='internal', nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_ticket_notes_tenant_id', 'ticket_notes', ['tenant_id'])
    op.create_index('ix_ticket_notes_ticket_id', 'ticket_notes', ['ticket_id'])

    # 3. Customer Feedback table
    op.create_table(
        'customer_feedback',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('channel', sa.String(length=32), server_default='web', nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('was_resolved', sa.Boolean(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_feedback_tenant_id', 'customer_feedback', ['tenant_id'])
    op.create_index('ix_feedback_ticket_id', 'customer_feedback', ['ticket_id'], unique=True)
    op.create_index('ix_feedback_token', 'customer_feedback', ['token'], unique=True)


def downgrade() -> None:
    op.drop_table('customer_feedback')
    op.drop_table('ticket_notes')
    op.drop_table('tickets')
