#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg
from oslo_utils import timeutils

from fuge import objects

periodic_opts = [
    cfg.IntOpt('service_down_time',
               default=180,
               help='Max interval size between periodic tasks execution in '
                    'seconds.'),
]

CONF = cfg.CONF
CONF.register_opts(periodic_opts)


class ServiceGroup(object):
    def __init__(self):
        self.service_down_time = CONF.service_down_time

    def service_is_up(self, member):
        if not isinstance(member, objects.Service):
            raise TypeError
        if member.get('forced_down'):
            return False

        last_heartbeat = (member.get(
            'last_seen_up') or member['updated_at'] or member['created_at'])
        now = timeutils.utcnow(True)
        elapsed = timeutils.delta_seconds(last_heartbeat, now)
        is_up = abs(elapsed) <= self.service_down_time
        return is_up
