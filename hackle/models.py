from sqlalchemy import Column, ForeignKey, Integer, Sequence, String, Text, UniqueConstraint, func, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

from .utils import Enum

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, nullable=False)
    email = Column(String(255), nullable=False)
    __table_args__ = (
        UniqueConstraint('email', name='_email'),
    )

sa_user = User.__table__


class DockerHost(Base):
    __tablename__ = 'docker_hosts'

    id = Column(Integer, Sequence('dh_id_seq'), primary_key=True, nullable=False)
    domain = Column(String(255), nullable=False)
    cert = Column(Text, nullable=False)
    key = Column(Text, nullable=False)
    __table_args__ = (
        UniqueConstraint('domain', name='_domain'),
    )

sa_docker_host = DockerHost.__table__


class Event(Base):
    __tablename__ = 'events'

    class Verbs(Enum):
        SIGN_IN = 'sign_in'
        CLONE = 'clone'

    id = Column(Integer, Sequence('event_id_seq'), primary_key=True, nullable=False)

    user = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    verb = Column(Verbs.sa_enum(), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    data = Column(JSONB)

event = Event.__table__
