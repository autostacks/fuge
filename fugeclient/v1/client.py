# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keystoneauth1 import loading
from keystoneauth1 import session as ksa_session

from fugeclient.common import httpclient
from fugeclient.v1 import services
from fugeclient.v1 import containers


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, fuge_url=None,
                 endpoint_type=None, service_type='container',
                 region_name=None, input_auth_token=None,
                 session=None, password=None, auth_type='password',
                 interface='publicURL', service_name=None, insecure=False,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None):

        # We have to keep the api_key are for backwards compat, but let's
        # remove it from the rest of our code since it's not a keystone
        # concept
        if not password:
            password = api_key
        # Backwards compat for people assing in endpoint_type
        if endpoint_type:
            interface = endpoint_type

        if fuge_url and input_auth_token:
            auth_type = 'admin_token'
            session = None
            loader_kwargs = dict(
                token=input_auth_token,
                endpoint=fuge_url)
        elif input_auth_token and not session:
            auth_type = 'token'
            loader_kwargs = dict(
                token=input_auth_token,
                auth_url=auth_url,
                project_id=project_id,
                project_name=project_name,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name)
        else:
            loader_kwargs = dict(
                username=username,
                password=password,
                auth_url=auth_url,
                project_id=project_id,
                project_name=project_name,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name)

        # Backwards compatibility for people not passing in Session
        if session is None:
            loader = loading.get_plugin_loader(auth_type)

            # This should be able to handle v2 and v3 Keystone Auth
            auth_plugin = loader.load_from_options(**loader_kwargs)
            session = ksa_session.Session(
                auth=auth_plugin, verify=(not insecure))

        client_kwargs = {}

        if fuge_url:
            client_kwargs['endpoint_override'] = fuge_url
        if not fuge_url:
            try:
                # Trigger an auth error so that we can throw the exception
                # we always have
                session.get_endpoint(
                    service_type=service_type,
                    service_name=service_name,
                    interface=interface,
                    region_name=region_name)
            except Exception:
                raise RuntimeError("Not Authorized")

        self.http_client = httpclient.SessionClient(
            service_type=service_type,
            service_name=service_name,
            interface=interface,
            region_name=region_name,
            session=session,
            **client_kwargs)
        self.services = services.ServiceManager(self.http_client)
        self.containers = containers.ContainerManager(self.http_client)

