# -*- encoding: utf-8 -*-
"""SQLAlchemy storage backend."""
import uuid

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_utils import strutils
from oslo_utils import timeutils
from oslo_utils import uuidutils
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from fuge.common import exception
from fuge.common.i18n import _
from fuge.db import api
from fuge.db.sqlalchemy import models

CONF = cfg.CONF


_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def generate_uuid():
    return str(uuid.uuid4())


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def add_show_deleted_filter(context, query):
    """Adds an show deleted filter to a query.
    :param context: The context from request.
    :param query: Initial query to add filter to.
    """
    if context.show_deleted:
        return query
    else:
        return query.filter_by(deleted=0)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(
            _('The sort_key value "%(key)s" is an invalid field for sorting')
            % {'key': sort_key})
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def _add_tenant_filters(self, context, query):
        if context.is_admin and context.all_tenants:
            return query

        if context.project_id:
            query = query.filter_by(project_id=context.project_id)
        else:
            query = query.filter_by(user_id=context.user_id)

        return query

    def destroy_service(self, service_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Service, session=session)
            query = add_identity_filter(query, service_id)
            count = query.delete()
            if count != 1:
                raise exception.ServiceNotFound(service_id)

    def update_service(self, service_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Service, session=session)
            query = add_identity_filter(query, service_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ServiceNotFound(service_id)

            if 'report_count' in values:
                if values['report_count'] > ref.report_count:
                    ref.last_seen_up = timeutils.utcnow()

            ref.update(values)
        return ref

    def get_service_by_host_and_binary(self, context, host, binary):
        query = model_query(models.Service)
        query = query.filter_by(host=host, binary=binary)
        query = add_show_deleted_filter(context, query)
        try:
            return query.one()
        except NoResultFound:
            return None

    def create_service(self, values):
        service = models.Service()
        service.update(values)
        try:
            service.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ServiceAlreadyExists(
                id=service['id'])
        return service

    def get_service_list(self, context, disabled=None, limit=None,
                             marker=None, sort_key=None, sort_dir=None
                             ):
        query = model_query(models.Service)
        query = add_show_deleted_filter(context, query)
        if disabled:
            query = query.filter_by(disabled=disabled)

        return _paginate_query(models.Service, limit, marker,
                               sort_key, sort_dir, query)

    def get_container_list(self, context, filters=None, limit=None,
                           marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Container)
        query = self._add_tenant_filters(context, query)
        query = add_show_deleted_filter(context, query)
        return _paginate_query(models.Container, limit, marker,
                               sort_key, sort_dir, query)

    def create_container(self, values):
        # ensure defaults are present for new containers
        if not values.get('uuid'):
            values['uuid'] = generate_uuid()

        container = models.Container()
        container.update(values)
        try:
            container.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ContainerAlreadyExists(uuid=values['uuid'])
        return container

    def get_container_by_id(self, context, container_id):
        query = model_query(models.Container)
        query = self._add_tenant_filters(context, query)
        query = add_show_deleted_filter(context, query)
        query = query.filter_by(id=container_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ContainerNotFound(container=container_id)

    def get_container_by_uuid(self, context, container_uuid):
        query = model_query(models.Container)
        query = self._add_tenant_filters(context, query)
        query = add_show_deleted_filter(context, query)
        query = query.filter_by(uuid=container_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ContainerNotFound(container=container_uuid)

    def get_container_by_name(self, context, container_name):
        query = model_query(models.Container)
        query = self._add_tenant_filters(context, query)
        query = add_show_deleted_filter(context, query)
        query = query.filter_by(name=container_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ContainerNotFound(container=container_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple containers exist with same '
                                     'name. Please use the container uuid '
                                     'instead.')

    def destroy_container(self, container_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Container, session=session)
            query = add_identity_filter(query, container_id)
            count = query.delete()
            if count != 1:
                raise exception.ContainerNotFound(container_id)

    def update_container(self, container_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Container.")
            raise exception.InvalidParameterValue(err=msg)

        session = get_session()
        with session.begin():
            query = model_query(models.Container, session=session)
            query = add_identity_filter(query, container_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ContainerNotFound(container=container_id)

            if 'provision_state' in values:
                values['provision_updated_at'] = timeutils.utcnow()

            ref.update(values)
        return ref

