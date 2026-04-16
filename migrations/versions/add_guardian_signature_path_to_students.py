"""add guardian_signature_path to students

Revision ID: a1b2c3d4e5f6
Revises: 737205b0dded
Create Date: 2026-04-15

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '737205b0dded'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('students',
        sa.Column('guardian_signature_path', sa.String(length=255), nullable=True)
    )


def downgrade():
    op.drop_column('students', 'guardian_signature_path')
