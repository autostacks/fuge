# -*- encoding: utf-8 -*-
"""Starter script for fuge-db-manage."""

from oslo_config import cfg

# from fuge.db import migration
from fuge.db.sqlalchemy import migration

CONF = cfg.CONF


def do_version():
    print('Current DB revision is %s' % migration.version())


def do_upgrade():
    migration.upgrade(CONF.command.revision)


def do_stamp():
    migration.stamp(CONF.command.revision)


def do_revision():
    migration.revision(message=CONF.command.message,
                       autogenerate=CONF.command.autogenerate)


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('version')
    parser.set_defaults(func=do_version)

    parser = subparsers.add_parser('upgrade')
    parser.add_argument('revision', nargs='?')
    parser.set_defaults(func=do_upgrade)

    parser = subparsers.add_parser('stamp')
    parser.add_argument('revision')
    parser.set_defaults(func=do_stamp)

    parser = subparsers.add_parser('revision')
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.set_defaults(func=do_revision)


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help='Available commands',
                                    handler=add_command_parsers)
    CONF.register_cli_opt(command_opt)

    CONF(project='fuge')
    CONF.command.func()
