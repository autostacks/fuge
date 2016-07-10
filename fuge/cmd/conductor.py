# -*- encoding: utf-8 -*-

"""Starter script for the Fuge conductor service."""

import os
import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

from fuge.common.i18n import _LI
from fuge.common import rpc_service
from fuge.common import service as fuge_service
from fuge.common import short_id
from fuge.conductor.handlers import compute as compute_handler

LOG = logging.getLogger(__name__)


def main():
    fuge_service.prepare_service(sys.argv)

    LOG.info(_LI('Starting server in PID %s'), os.getpid())
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    cfg.CONF.import_opt('topic', 'fuge.conductor.config', group='conductor')

    conductor_id = short_id.generate_id()
    endpoints = [
        compute_handler.Handler(),
    ]

    server = rpc_service.Service.create(cfg.CONF.conductor.topic,
                                        conductor_id, endpoints,
                                        binary='fuge-conductor')
    launcher = service.launch(cfg.CONF, server)
    launcher.wait()
