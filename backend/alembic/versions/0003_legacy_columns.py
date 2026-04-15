"""legacy missing columns

Revision ID: 0003_legacy_columns
Revises: 0002_legacy_compat
Create Date: 2026-04-13 00:45:00
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_legacy_columns"
down_revision: Union[str, None] = "0002_legacy_compat"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS role VARCHAR(32) DEFAULT 'user' NOT NULL")
    op.execute("ALTER TABLE IF EXISTS chats ADD COLUMN IF NOT EXISTS title VARCHAR(255)")
    op.execute("ALTER TABLE IF EXISTS messages ADD COLUMN IF NOT EXISTS risk_level VARCHAR(16)")
    op.execute("ALTER TABLE IF EXISTS messages ADD COLUMN IF NOT EXISTS language VARCHAR(8)")


def downgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS messages DROP COLUMN IF EXISTS language")
    op.execute("ALTER TABLE IF EXISTS messages DROP COLUMN IF EXISTS risk_level")
    op.execute("ALTER TABLE IF EXISTS chats DROP COLUMN IF EXISTS title")
