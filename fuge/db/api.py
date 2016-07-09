# -*- encoding: utf-8 -*-
"""
Base classes for storage engines
"""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'fuge.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def destroy_service(self, service_id):
        """Destroys a service record.

        :param service_id: The id of a service.
        """

    @abc.abstractmethod
    def update_service(self, service_id, values):
        """Update properties of a service.

        :param service_id: The id of a service record.
        """

    @abc.abstractmethod
    def get_service_by_host_and_binary(self, context, host, binary):
        """Return a service record.

        :param context: The security context
        :param host: The host where the binary is located.
        :param binary: The name of the binary.
        :returns: A service record.
        """

    @abc.abstractmethod
    def create_service(self, values):
        """Create a new service record.

        :param values: A dict containing several items used to identify
                       and define the service record.
        :returns: A service record.
        """

    @abc.abstractmethod
    def get_service_list(self, context, disabled=None, limit=None,
                             marker=None, sort_key=None, sort_dir=None):
        """Get matching service records.

        Return a list of the specified columns for all services
        those match the specified filters.

        :param context: The security context
        :param disabled: Filters disbaled services. Defaults to None.
        :param limit: Maximum number of services to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """

    @abc.abstractmethod
    def get_container_list(self, context, filters=None,
                           limit=None, marker=None, sort_key=None,
                           sort_dir=None):
        """Get matching containers.

        Return a list of the specified columns for all containers that match
        the specified filters.

        :param context: The security context
        :param filters: Filters to apply. Defaults to None.

        :param limit: Maximum number of containers to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """

    @abc.abstractmethod
    def create_container(self, values):
        """Create a new container.

        :param values: A dict containing several items used to identify
                       and track the container, and several dicts which are
                       passed
                       into the Drivers when managing this container. For
                       example:

                       ::

                        {
                         'uuid': utils.generate_uuid(),
                         'name': 'example',
                         'type': 'virt'
                        }
        :returns: A container.
        """

    @abc.abstractmethod
    def get_container_by_id(self, context, container_id):
        """Return a container.

        :param context: The security context
        :param container_id: The id of a container.
        :returns: A container.
        """

    @abc.abstractmethod
    def get_container_by_uuid(self, context, container_uuid):
        """Return a container.

        :param context: The security context
        :param container_uuid: The uuid of a container.
        :returns: A container.
        """

    @abc.abstractmethod
    def get_container_by_name(self, context, container_name):
        """Return a container.

        :param context: The security context
        :param container_name: The name of a container.
        :returns: A container.
        """

    @abc.abstractmethod
    def destroy_container(self, container_id):
        """Destroy a container and all associated interfaces.

        :param container_id: The id or uuid of a container.
        """

    @abc.abstractmethod
    def update_container(self, container_id, values):
        """Update properties of a container.

        :param container_id: The id or uuid of a container.
        :returns: A container.
        :raises: ContainerNotFound
        """
