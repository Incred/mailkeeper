import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func

from lib import asynccontextmanager

Base = declarative_base()

class DB:
    def __init__(self, url):
        self._url = url
        self.engine = None

    def connect(self):
        self.engine = create_async_engine(self._url)

    @asynccontextmanager
    async def session(self, *args, **kwargs):
        ASession = sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        new_session = ASession(*args, **kwargs)
        try:
            yield new_session
            await new_session.commit()
        except Exception as exc:
            await new_session.rollback()
            raise
        finally:
            await new_session.close()


class Email(Base):
    __tablename__ = 'mailkeeper_email'

    id = Column(Integer, primary_key=True)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=False)
    subject = Column(String(255), nullable=False)
    created = Column(DateTime(timezone=True),)
    inbound = Column(Boolean, nullable=True)
    bounced = Column(Boolean, nullable=True)
    message_id = Column(String(255), nullable=True)
