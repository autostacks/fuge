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

"""Fuge Service Layer"""

from oslo_log import log
from oslo_service import periodic_task

from fuge import objects
from fuge.service import periodic


LOG = log.getLogger(__name__)


class ServicePeriodicTasks(periodic_task.PeriodicTasks):
    '''Fuge periodic Task class

    Any periodic task job need to be added into this class
    '''

    def __init__(self, conf, binary):
        self.fuge_service_ref = None
        self.host = conf.host
        self.binary = binary
        super(ServicePeriodicTasks, self).__init__(conf)

    @periodic_task.periodic_task(run_immediately=True)
    @periodic.set_context
    def update_fuge_service(self, ctx):
        LOG.debug('Update fuge_service')
        if self.fuge_service_ref is None:
            self.fuge_service_ref = \
                objects.Service.get_by_host_and_binary(
                    ctx, self.host, self.binary)
            if self.fuge_service_ref is None:
                fuge_service_dict = {
                    'host': self.host,
                    'binary': self.binary
                }
                self.fuge_service_ref = objects.Service(
                    ctx, **fuge_service_dict)
                self.fuge_service_ref.create()
        self.fuge_service_ref.report_state_up()


def setup(conf, binary, tg):
    pt = ServicePeriodicTasks(conf, binary)
    tg.add_dynamic_timer(
        pt.run_periodic_tasks,
        periodic_interval_max=conf.periodic_interval_max,
        context=None)
