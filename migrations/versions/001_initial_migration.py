"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buildings_id'), 'buildings', ['id'], unique=False)
    
    op.create_table('activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['activities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    op.create_index(op.f('ix_activities_name'), 'activities', ['name'], unique=False)
    
    op.create_table('phones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phones_id'), 'phones', ['id'], unique=False)
    
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('building_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    
    op.create_table('organization_activity',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('organization_id', 'activity_id')
    )
    
    op.create_table('organization_phone',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('phone_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['phone_id'], ['phones.id'], ),
        sa.PrimaryKeyConstraint('organization_id', 'phone_id')
    )


def downgrade() -> None:
    op.drop_table('organization_phone')
    op.drop_table('organization_activity')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_phones_id'), table_name='phones')
    op.drop_table('phones')
    op.drop_index(op.f('ix_activities_name'), table_name='activities')
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_buildings_id'), table_name='buildings')
    op.drop_table('buildings')