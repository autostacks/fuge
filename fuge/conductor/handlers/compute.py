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

"""Fuge Conductor default handler."""


# These are the database operations - They are executed by the conductor
# service.  API calls via AMQP trigger the handlers to be called.
import logging


LOG = logging.getLogger(__name__)


class Handler(object):
    def __init__(self):
        super(Handler, self).__init__()

    def container_create(self, context, container):
        return container

    def container_delete(self, container_uuid):
        pass

    def container_show(self, container_uuid):
        pass

    def container_reboot(self, container_uuid):
        pass

    def container_stop(self, container_uuid):
        pass

    def container_start(self, container_uuid):
        pass

    def container_pause(self, container_uuid):
        pass

    def container_unpause(self, container_uuid):
        pass

    def container_logs(self, container_uuid):
        return self._call('container_logs', container_uuid=container_uuid)

    def container_exec(self, container_uuid, command):
        return self._call('container_exec', container_uuid=container_uuid,
                          command=command)