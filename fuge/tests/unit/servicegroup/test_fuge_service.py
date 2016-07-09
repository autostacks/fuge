# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from fuge.common.rpc_service import CONF
from fuge import objects
from fuge.servicegroup import service_periodic as periodic
from fuge.tests import base


class ServicePeriodicTestCase(base.BaseTestCase):
    def setUp(self):
        super(ServicePeriodicTestCase, self).setUp()
        mock_fuge_service_refresh = mock.Mock()

        class FakeSrv(object):
            report_state_up = mock_fuge_service_refresh

        self.fake_srv = FakeSrv()
        self.fake_srv_refresh = mock_fuge_service_refresh

    @mock.patch.object(objects.Service, 'get_by_host_and_binary')
    @mock.patch.object(objects.Service, 'create')
    @mock.patch.object(objects.Service, 'report_state_up')
    def test_update_fuge_service_firsttime(self,
                                          mock_srv_refresh,
                                          mock_srv_create,
                                          mock_srv_get
                                          ):
        p_task = periodic.ServicePeriodicTasks(CONF,
                                                  'fake-conductor')
        mock_srv_get.return_value = None

        p_task.update_fuge_service(None)

        mock_srv_get.assert_called_once_with(mock.ANY, p_task.host,
                                             p_task.binary)
        mock_srv_create.assert_called_once_with()
        mock_srv_refresh.assert_called_once_with()

    @mock.patch.object(objects.Service, 'get_by_host_and_binary')
    @mock.patch.object(objects.Service, 'create')
    def test_update_fuge_service_on_restart(self,
                                           mock_srv_create,
                                           mock_srv_get):
        p_task = periodic.ServicePeriodicTasks(CONF,
                                                  'fake-conductor')
        mock_srv_get.return_value = self.fake_srv

        p_task.update_fuge_service(None)

        mock_srv_get.assert_called_once_with(mock.ANY, p_task.host,
                                             p_task.binary)
        self.fake_srv_refresh.assert_called_once_with()

    def test_update_fuge_service_regular(self):
        p_task = periodic.ServicePeriodicTasks(CONF,
                                                  'fake-conductor')
        p_task.fuge_service_ref = self.fake_srv

        p_task.update_fuge_service(None)

        self.fake_srv_refresh.assert_called_once_with()
