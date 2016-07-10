#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""API for interfacing with Fuge Backend."""
import logging
from oslo_config import cfg

from fuge.common import rpc_service


LOG = logging.getLogger(__name__)
# The Backend API class serves as a AMQP client for communicating
# on a topic exchange specific to the conductors.  This allows the ReST
# API to trigger operations on the conductors


class API(rpc_service.API):
    def __init__(self, transport=None, context=None, topic=None):
        if topic is None:
            cfg.CONF.import_opt('topic', 'fuge.conductor.config',
                                group='conductor')
        super(API, self).__init__(transport, context,
                                  topic=cfg.CONF.conductor.topic)

    # NOTE(vivek): Add all APIs here
    def container_create(self, container):
        return self._call('container_create', container=container)

    def container_delete(self, container_uuid):
        return self._call('container_delete', container_uuid=container_uuid)

    def container_show(self, container_uuid):
        return self._call('container_show', container_uuid=container_uuid)

    def container_reboot(self, container_uuid):
        return self._call('container_reboot', container_uuid=container_uuid)

    def container_stop(self, container_uuid):
        return self._call('container_stop', container_uuid=container_uuid)

    def container_start(self, container_uuid):
        return self._call('container_start', container_uuid=container_uuid)

    def container_pause(self, container_uuid):
        return self._call('container_pause', container_uuid=container_uuid)

    def container_unpause(self, container_uuid):
        return self._call('container_unpause', container_uuid=container_uuid)

    def container_logs(self, container_uuid):
        return self._call('container_logs', container_uuid=container_uuid)

    def container_exec(self, container_uuid, command):
        return self._call('container_exec', container_uuid=container_uuid,
                          command=command)
