# -*- encoding: utf-8 -*-
import os
import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

from fuge.common.i18n import _LI
from fuge.common import rpc_service
from fuge.common import service as fuge_service
from fuge.common import short_id
from fuge.compute import manager as compute_manager

LOG = logging.getLogger(__name__)


def main():
    fuge_service.prepare_service(sys.argv)

    LOG.info(_LI('Starting server in PID %s'), os.getpid())
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    cfg.CONF.import_opt('topic', 'fuge.compute.config', group='compute')

    compute_id = short_id.generate_id()
    endpoints = [
        compute_manager.Manager(),
    ]

    server = rpc_service.Service.create(cfg.CONF.compute.topic, compute_id,
                                        endpoints, binary='fuge-compute')
    launcher = service.launch(cfg.CONF, server)
    launcher.wait()
