# Copyright 2015 NEC Corporation.  All rights reserved.
#
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


from fugeclient.common import cliutils as utils
from fugeclient.common import utils as fuge_utils


def do_service_list(cs, args):
    """Print a list of fuge services."""
    services = cs.services.list()
    columns = ('id', 'host', 'binary', 'state')
    utils.print_list(services, columns,
                     {'versions': fuge_utils.print_list_field('versions')})
