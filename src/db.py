from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from src.config import config


engine = create_engine(
    url=config.env_data.DB_URL_SYNC,
    echo=True,
    connect_args={
        "options": "-c lc_messages=en_US.UTF-8"
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_session():
    with SessionLocal() as session:
        yield session
        session.commit()


class Base(DeclarativeBase):
    pass