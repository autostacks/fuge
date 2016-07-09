# -*- encoding: utf-8 -*-
from oslo_config import cfg
from oslo_db import options

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine to use.')
]

cfg.CONF.register_opts(sql_opts, 'database')
options.set_defaults(cfg.CONF)
