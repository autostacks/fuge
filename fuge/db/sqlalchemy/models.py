# -*- encoding: utf-8 -*-
"""
SQLAlchemy models for container service
"""

import json

from oslo_config import cfg
from oslo_db.sqlalchemy import models
import six.moves.urllib.parse as urlparse
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator, TEXT


def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JsonEncodedType(TypeDecorator):
    """Abstract base type serialized as json-encoded string in db."""
    type = None
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            # Save default value according to current type to keep the
            # interface the consistent.
            value = self.type()
        elif not isinstance(value, self.type):
            raise TypeError("%s supposes to store %s objects, but %s given"
                            % (self.__class__.__name__,
                               self.type.__name__,
                               type(value).__name__))
        serialized_value = json.dumps(value)
        return serialized_value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class JSONEncodedDict(JsonEncodedType):
    """Represents dict serialized as json-encoded string in db."""
    type = dict


class JSONEncodedList(JsonEncodedType):
    """Represents list serialized as json-encoded string in db."""
    type = list


class FugeBase(models.TimestampMixin,
               models.SoftDeleteMixin,
               models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    def save(self, session=None):
        import fuge.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(FugeBase, self).save(session)


Base = declarative_base(cls=FugeBase)


class Service(Base):
    """Represents health status of various fuge services"""
    __tablename__ = 'services'
    __table_args__ = (
        schema.UniqueConstraint("host", "binary",
                                name="uniq_services0host0binary"),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    host = Column(String(255))
    binary = Column(String(255))
    disabled = Column(Boolean, default=False)
    disabled_reason = Column(String(255))
    last_seen_up = Column(DateTime, nullable=True)
    forced_down = Column(Boolean, default=False)
    report_count = Column(Integer, nullable=False, default=0)


class Container(Base):
    """Represents a container."""
    __tablename__ = 'containers'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_containers0uuid'),
        table_args()
    )
    id = Column(Integer, primary_key=True)
    project_id = Column(String(255))
    user_id = Column(String(255))
    uuid = Column(String(36))
    name = Column(String(255))
    image = Column(String(255))
    command = Column(String(255))
    status = Column(String(20))
    memory = Column(String(255))
    environment = Column(JSONEncodedDict)
