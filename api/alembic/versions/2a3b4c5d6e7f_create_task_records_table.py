"""create_task_records_table

Revision ID: 2a3b4c5d6e7f
Revises: 488ca7d5c88f
Create Date: 2026-05-13 12:35:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, Sequence[str], None] = '488ca7d5c88f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create table using raw SQL to avoid enum creation issues
    op.execute("""
        CREATE TABLE task_records (
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            id UUID NOT NULL,
            task_id VARCHAR NOT NULL,
            task_name VARCHAR NOT NULL,
            args JSON,
            kwargs JSON,
            status taskstatus NOT NULL,
            result JSON,
            error TEXT,
            worker_hostname VARCHAR,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            related_record_id UUID,
            created_by UUID NOT NULL,
            updated_by UUID,
            PRIMARY KEY (id)
        )
    """)

    # Create indexes
    op.create_index(op.f('ix_task_records_task_id'), 'task_records', ['task_id'], unique=True)
    op.create_index(op.f('ix_task_records_task_name'), 'task_records', ['task_name'], unique=False)
    op.create_index(op.f('ix_task_records_status'), 'task_records', ['status'], unique=False)
    op.create_index(
        op.f('ix_task_records_related_record_id'),
        'task_records',
        ['related_record_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_task_records_related_record_id'), table_name='task_records')
    op.drop_index(op.f('ix_task_records_status'), table_name='task_records')
    op.drop_index(op.f('ix_task_records_task_name'), table_name='task_records')
    op.drop_index(op.f('ix_task_records_task_id'), table_name='task_records')
    op.drop_table('task_records')
    # Don't drop enum type as it might be used by other tables
