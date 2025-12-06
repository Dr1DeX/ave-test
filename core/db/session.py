from contextvars import ContextVar, Token
from functools import wraps
from typing import Union
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


engine = create_async_engine(
    config.DATABASE_CONNECTION_URL,
    pool_recycle=3600,
    pool_size=config.DATABASE_POOL_SIZE,
    max_overflow=config.DATABASE_MAX_OVERFLOW,
    echo=config.DATABASE_ECHO,
)

async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)
Base = declarative_base()


async def init_db():
    return session


def async_alchemy_context_decorator(handler):
    """Sharable-session component"""

    @wraps(handler)
    async def context_decorator(*args, **kwargs):
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)
        try:
            result = await handler(*args, **kwargs)
        finally:
            await session.remove()
            reset_session_context(context=context)
        return result

    return context_decorator
