from logging.config import fileConfig

from alembic import context

from app import models  # noqa: F401  registra las tablas en Base.metadata
from app.database import Base, engine, url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# La conexión sale de app/config.py (.env), no de alembic.ini: así no hay credenciales en el repo.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse (alembic upgrade --sql), útil para revisarlo antes de aplicarlo."""
    context.configure(
        url=url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
