"""baseline existing schema

Revision ID: 81e81464848c
Revises: 
Create Date: 2026-03-11 12:11:47.468656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81e81464848c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('market_data'):
        op.create_table(
            'market_data',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.Column('close_price', sa.Float(), nullable=True),
            sa.Column('volume', sa.Integer(), nullable=True),
            sa.Column('volatility', sa.Float(), nullable=True),
            sa.Column('atr', sa.Float(), nullable=True),
            sa.Column('ema20', sa.Float(), nullable=True),
            sa.Column('ema50', sa.Float(), nullable=True),
            sa.Column('ema200', sa.Float(), nullable=True),
            sa.Column('rsi', sa.Float(), nullable=True),
            sa.Column('tags', sa.String(length=200), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if not inspector.has_table('alert'):
        op.create_table(
            'alert',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.Column('alert_type', sa.String(length=50), nullable=True),
            sa.Column('message', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if not inspector.has_table('options_data'):
        op.create_table(
            'options_data',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.Column('spot_price', sa.Float(), nullable=True),
            sa.Column('calls_count', sa.Integer(), nullable=True),
            sa.Column('puts_count', sa.Integer(), nullable=True),
            sa.Column('avg_call_iv', sa.Float(), nullable=True),
            sa.Column('avg_put_iv', sa.Float(), nullable=True),
            sa.Column('nearest_expiration', sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if not inspector.has_table('paper_position'):
        op.create_table(
            'paper_position',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=False),
            sa.Column('strategy', sa.String(length=50), nullable=False),
            sa.Column('entry_time', sa.DateTime(), nullable=True),
            sa.Column('entry_price', sa.Float(), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('stop_loss', sa.Float(), nullable=True),
            sa.Column('target_price', sa.Float(), nullable=True),
            sa.Column('current_price', sa.Float(), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.Column('entry_reason', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('symbol'),
        )

    if not inspector.has_table('paper_trade'):
        op.create_table(
            'paper_trade',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=False),
            sa.Column('strategy', sa.String(length=50), nullable=False),
            sa.Column('entry_time', sa.DateTime(), nullable=False),
            sa.Column('exit_time', sa.DateTime(), nullable=True),
            sa.Column('entry_price', sa.Float(), nullable=False),
            sa.Column('exit_price', sa.Float(), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('realized_pnl', sa.Float(), nullable=False),
            sa.Column('realized_pct', sa.Float(), nullable=False),
            sa.Column('entry_reason', sa.Text(), nullable=True),
            sa.Column('exit_reason', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('paper_trade'):
        op.drop_table('paper_trade')

    if inspector.has_table('paper_position'):
        op.drop_table('paper_position')

    if inspector.has_table('options_data'):
        op.drop_table('options_data')

    if inspector.has_table('alert'):
        op.drop_table('alert')

    if inspector.has_table('market_data'):
        op.drop_table('market_data')
