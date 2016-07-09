#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_versionedobjects import fields

from fuge.db import api as dbapi
from fuge.objects import base


@base.FugeObjectRegistry.register
class Service(base.FugePersistentObject, base.FugeObject,
                 base.FugeObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': fields.IntegerField(),
        'host': fields.StringField(nullable=True),
        'binary': fields.StringField(nullable=True),
        'disabled': fields.BooleanField(),
        'disabled_reason': fields.StringField(nullable=True),
        'last_seen_up': fields.DateTimeField(nullable=True),
        'forced_down': fields.BooleanField(),
        'report_count': fields.IntegerField(),
    }

    @staticmethod
    def _from_db_object(service, db_service):
        """Converts a database entity to a formal object."""
        for field in service.fields:
            service[field] = db_service[field]

        service.obj_reset_changes()
        return service

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [Service._from_db_object(cls(context), obj)
                for obj in db_objects]

    @base.remotable_classmethod
    def get_by_host_and_binary(cls, context, host, binary):
        """Find a service based on its hostname and binary.

        :param host: The host on which the binary is running.
        :param binary: The name of the binary.
        :param context: Security context.
        :returns: a :class:`Service` object.
        """
        db_service = cls.dbapi.get_service_by_host_and_binary(
            context, host, binary)
        if db_service is None:
            return None
        service = Service._from_db_object(cls(context), db_service)
        return service

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None):
        """Return a list of Service objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`Service` object.

        """
        db_services = cls.dbapi.get_service_list(
            context, limit=limit, marker=marker, sort_key=sort_key,
            sort_dir=sort_dir)
        return Service._from_db_object_list(db_services, cls,
                                               context)

    @base.remotable
    def create(self, context=None):
        """Create a Service record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Service(context)
        """
        values = self.obj_get_changes()
        db_service = self.dbapi.create_service(values)
        self._from_db_object(self, db_service)

    @base.remotable
    def destroy(self, context=None):
        """Delete the Service from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Service(context)
        """
        self.dbapi.destroy_service(self.id)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this Service.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Service(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_service(self.id, updates)
        self.obj_reset_changes()

    @base.remotable
    def report_state_up(self, context=None):
        """Touching the service record to show aliveness.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Service(context)
        """
        self.report_count += 1
        self.save()
