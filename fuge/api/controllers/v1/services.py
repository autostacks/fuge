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

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes

from fuge.api.controllers import base
from fuge.api.controllers.v1 import collection
from fuge.api.controllers.v1 import types
from fuge.api import expose
from fuge.api import servicegroup as svcgrp_api
from fuge.common import policy
from fuge import objects


class Service(base.APIBase):

    host = wtypes.text
    """Name of the host """

    binary = wtypes.text
    """Name of the binary"""

    state = wtypes.text
    """State of the binary"""

    id = wsme.wsattr(wtypes.IntegerType(minimum=1))
    """The id for the healthcheck record """

    report_count = wsme.wsattr(wtypes.IntegerType(minimum=0))
    """The number of times the heartbeat was reported """

    disabled = types.boolean
    """If the service is 'disabled' administratively """

    disabled_reason = wtypes.text
    """Reason for disabling """

    def __init__(self, state, **kwargs):
        super(Service, self).__init__()

        self.fields = ['state']
        setattr(self, 'state', state)
        for field in objects.Service.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))


class ServiceCollection(collection.Collection):

    services = [Service]
    """A list containing bays objects"""

    def __init__(self, **kwargs):
        super(ServiceCollection, self).__init__()
        self._type = 'services'

    @staticmethod
    def convert_db_rec_list_to_collection(service_group_api,
                                          rpc_services, **kwargs):
        collection = ServiceCollection()
        collection.services = []
        for p in rpc_services:
            alive = service_group_api.service_is_up(p)
            state = 'up' if alive else 'down'
            msvc = Service(state, **p.as_dict())
            collection.services.append(msvc)
        collection.next = collection.get_next(limit=None, url=None, **kwargs)
        return collection


class ServicesController(rest.RestController):
    """REST controller for fuge services."""

    def __init__(self, **kwargs):
        super(ServicesController, self).__init__()
        self.service_group_api = svcgrp_api.ServiceGroup()

    @expose.expose(ServiceCollection)
    @policy.enforce_wsgi("service")
    def get_all(self):
        """Retrieve a list of fuge service.

        """
        services = objects.Service.list(pecan.request.context,
                                        limit=None,
                                        marker=None,
                                        sort_key='id',
                                        sort_dir='asc')
        return ServiceCollection.convert_db_rec_list_to_collection(
            self.service_group_api, services)
