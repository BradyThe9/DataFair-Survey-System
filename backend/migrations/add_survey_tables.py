# backend/migrations/add_survey_tables.py
"""Add survey system tables

Revision ID: survey_001
Revises: 
Create Date: 2025-06-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'survey_001'
down_revision = None  # Set this to your latest migration ID
branch_labels = None
depends_on = None


def upgrade():
    """Create survey system tables"""
    
    # Create surveys table
    op.create_table('surveys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('base_reward', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('estimated_duration', sa.Integer(), nullable=False),
        sa.Column('qualification_criteria', sa.JSON(), nullable=True),
        sa.Column('questions', sa.JSON(), nullable=False),
        sa.Column('max_responses', sa.Integer(), nullable=True),
        sa.Column('current_responses', sa.Integer(), nullable=True, default=0),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create survey_responses table
    op.create_table('survey_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('survey_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('qualification_passed', sa.Boolean(), nullable=True, default=False),
        sa.Column('completion_percentage', sa.Integer(), nullable=True, default=0),
        sa.Column('earnings_amount', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0.00),
        sa.Column('started_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('survey_id', 'user_id', name='unique_user_survey')
    )
    
    # Create qualification_responses table
    op.create_table('qualification_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('survey_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('qualified', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_surveys_status', 'surveys', ['status'])
    op.create_index('idx_surveys_category', 'surveys', ['category'])
    op.create_index('idx_surveys_expires_at', 'surveys', ['expires_at'])
    op.create_index('idx_survey_responses_user', 'survey_responses', ['user_id'])
    op.create_index('idx_survey_responses_survey', 'survey_responses', ['survey_id'])
    op.create_index('idx_survey_responses_completed', 'survey_responses', ['completed_at'])
    op.create_index('idx_qualification_responses_user', 'qualification_responses', ['user_id'])


def downgrade():
    """Drop survey system tables"""
    
    # Drop indexes
    op.drop_index('idx_qualification_responses_user', table_name='qualification_responses')
    op.drop_index('idx_survey_responses_completed', table_name='survey_responses')
    op.drop_index('idx_survey_responses_survey', table_name='survey_responses')
    op.drop_index('idx_survey_responses_user', table_name='survey_responses')
    op.drop_index('idx_surveys_expires_at', table_name='surveys')
    op.drop_index('idx_surveys_category', table_name='surveys')
    op.drop_index('idx_surveys_status', table_name='surveys')
    
    # Drop tables
    op.drop_table('qualification_responses')
    op.drop_table('survey_responses')
    op.drop_table('surveys')