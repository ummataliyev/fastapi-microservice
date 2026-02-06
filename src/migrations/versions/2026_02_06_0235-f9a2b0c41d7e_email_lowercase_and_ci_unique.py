"""
enforce lowercase and case-insensitive unique email
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision: str = "f9a2b0c41d7e"
down_revision: Union[str, Sequence[str], None] = "3fe16a2abf4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_check_constraint(
    connection: Connection,
    table_name: str,
    constraint_name: str,
) -> bool:
    """
    Check whether a named CHECK constraint already exists on a table.

    :param connection: Active SQLAlchemy connection.
    :type connection: Connection
    :param table_name: Database table name.
    :type table_name: str
    :param constraint_name: Constraint name to verify.
    :type constraint_name: str
    :return: True when the constraint exists, otherwise False.
    :rtype: bool
    :raises Exception: If metadata inspection fails unexpectedly.
    """
    inspector = sa.inspect(connection)
    constraints = inspector.get_check_constraints(table_name)
    return any(item.get("name") == constraint_name for item in constraints)


def _has_index(
    connection: Connection,
    table_name: str,
    index_name: str,
) -> bool:
    """
    Check whether a named index already exists on a table.

    :param connection: Active SQLAlchemy connection.
    :type connection: Connection
    :param table_name: Database table name.
    :type table_name: str
    :param index_name: Index name to verify.
    :type index_name: str
    :return: True when the index exists, otherwise False.
    :rtype: bool
    :raises Exception: If metadata inspection fails unexpectedly.
    """
    inspector = sa.inspect(connection)
    indexes = inspector.get_indexes(table_name)
    return any(item.get("name") == index_name for item in indexes)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    user_table = sa.table(
        "user",
        sa.column("email", sa.String(length=255)),
    )

    if _has_index(bind, "user", op.f("ix_user_email")):
        op.drop_index(op.f("ix_user_email"), table_name="user")
    if not _has_index(bind, "user", op.f("ix_user_email")):
        op.create_index(op.f("ix_user_email"), "user", ["email"], unique=False)
    op.execute(
        sa.update(user_table)
        .where(user_table.c.email != sa.func.lower(user_table.c.email))
        .values(email=sa.func.lower(user_table.c.email))
    )

    duplicates_stmt = (
        sa.select(
            sa.func.lower(user_table.c.email).label("normalized_email"),
            sa.func.count().label("cnt"),
        )
        .group_by(sa.func.lower(user_table.c.email))
        .having(sa.func.count() > 1)
        .order_by(sa.func.count().desc(), sa.func.lower(user_table.c.email))
    )
    duplicates = bind.execute(duplicates_stmt).mappings().all()
    if duplicates:
        sample = ", ".join(item["normalized_email"] for item in duplicates[:5])
        raise RuntimeError(
            "Cannot enforce case-insensitive unique emails. "
            f"Resolve duplicate emails first (e.g. {sample})."
        )
    if not _has_check_constraint(bind, "user", "ck_user_email_lowercase"):
        op.create_check_constraint(
            "ck_user_email_lowercase",
            "user",
            "email = lower(email)",
        )
    if not _has_index(bind, "user", "uq_user_email_lower"):
        if dialect_name == "mysql":
            op.create_index("uq_user_email_lower", "user", ["email"], unique=True)
        else:
            op.create_index(
                "uq_user_email_lower",
                "user",
                [sa.text("lower(email)")],
                unique=True,
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if _has_index(bind, "user", "uq_user_email_lower"):
        op.drop_index("uq_user_email_lower", table_name="user")
    if _has_check_constraint(bind, "user", "ck_user_email_lowercase"):
        op.drop_constraint("ck_user_email_lowercase", "user", type_="check")
    if _has_index(bind, "user", op.f("ix_user_email")):
        op.drop_index(op.f("ix_user_email"), table_name="user")
    if not _has_index(bind, "user", op.f("ix_user_email")):
        op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
