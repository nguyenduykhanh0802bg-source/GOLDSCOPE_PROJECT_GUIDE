"""Alembic environment.

URL precedence: `-x url=...` / programmatic `sqlalchemy.url`, then DATABASE_URL via Settings.
Errors never echo the URL.
"""

from __future__ import annotations

from alembic import context

from goldscope.core.errors import ConfigError
from goldscope.core.settings import load_settings
from goldscope.db.models import Base
from goldscope.db.session import create_db_engine, normalize_url

config = context.config
target_metadata = Base.metadata


def _database_url() -> str:
    explicit = context.get_x_argument(as_dictionary=True).get("url") or config.get_main_option(
        "sqlalchemy.url"
    )
    if explicit:
        return normalize_url(explicit)
    settings = load_settings()
    if settings.database_url is None:
        raise ConfigError("DATABASE_URL is required to run migrations but is not set")
    return normalize_url(settings.database_url)


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_db_engine(_database_url())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
