# -*- encoding: utf-8 -*-

"""The Fuge Service API."""

import sys

from oslo_config import cfg

from fuge.common import service as fuge_service

CONF = cfg.CONF


def main():
    # Parse config file and command line options, then start logging
    fuge_service.prepare_service(sys.argv)

    # Enable object backporting via the conductor
    # TODO(yuanying): Uncomment after rpc services are implemented
    # base.fugeObject.indirection_api = base.fugeObjectIndirectionAPI()

    # Build and start the WSGI app
    launcher = fuge_service.process_launcher()
    server = fuge_service.WSGIService(
        'fuge_api',
        CONF.api.enable_ssl_api
    )
    launcher.launch_service(server, workers=server.workers)
    launcher.wait()

if __name__ == '__main__':
    sys.exit(main())
