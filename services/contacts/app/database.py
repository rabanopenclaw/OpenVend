from __future__ import annotations

import os
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    return os.getenv(
        "CONTACTS_DATABASE_URL",
        "postgresql+pg8000://openvend:openvend-dev-password@postgres:5432/contacts",
    )


@lru_cache
def get_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session]:
    session_factory = get_session_factory()
    with session_factory() as session:
        yield session
