"""Add allowed_all_classes to students and student_schedules table

Revision ID: a1b2c3d4e5f6
Revises: 510d2c8b0f6c
Create Date: 2026-04-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '510d2c8b0f6c'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columna allowed_all_classes a students
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'allowed_all_classes',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        ))

    # Crear tabla de asociación student_schedules (si no existe)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'student_schedules' not in inspector.get_table_names():
        op.create_table(
            'student_schedules',
            sa.Column('student_id', sa.Integer(),
                      sa.ForeignKey('students.id', ondelete='CASCADE'),
                      primary_key=True, nullable=False),
            sa.Column('schedule_id', sa.Integer(),
                      sa.ForeignKey('schedules.id', ondelete='CASCADE'),
                      primary_key=True, nullable=False),
        )


def downgrade():
    # Eliminar tabla de asociación
    op.drop_table('student_schedules')

    # Eliminar columna allowed_all_classes
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.drop_column('allowed_all_classes')
