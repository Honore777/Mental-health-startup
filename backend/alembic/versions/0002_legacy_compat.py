"""legacy schema compatibility

Revision ID: 0002_legacy_compat
Revises: 0001_initial
Create Date: 2026-04-13 00:30:00
"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_legacy_compat"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at TIMESTAMPTZ NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_sessions_user_id ON sessions (user_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_chats_user_id ON chats (user_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY,
            chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
            role VARCHAR(32) NOT NULL,
            content TEXT NOT NULL,
            risk_level VARCHAR(16),
            language VARCHAR(8),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_messages_chat_id ON messages (chat_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_messages_chat_id")
    op.execute("DROP TABLE IF EXISTS messages")
    op.execute("DROP INDEX IF EXISTS ix_chats_user_id")
    op.execute("DROP TABLE IF EXISTS chats")
    op.execute("DROP INDEX IF EXISTS ix_sessions_user_id")
    op.execute("DROP TABLE IF EXISTS sessions")
