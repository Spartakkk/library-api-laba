from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from app.config import DATABASE_URL
from app.models import Base

config = context.config
fileConfig(config.config_file_name, disable_existing_loggers=False)

url = config.get_main_option("sqlalchemy.url") or DATABASE_URL

target_metadata = Base.metadata

engine = create_engine(url)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
