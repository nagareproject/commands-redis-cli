# --
# Copyright (c) 2008-2024 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import sys

from iredis import entry, config

from nagare.admin import command
from nagare.services.redis import Redis

Redis.CONFIG_SPEC['cli'] = {
    'raw': 'boolean(default=True, help="use raw formatting for replies")',
    'completer_max': 'integer(default=300,help="completions cache length")',
    'completion_casing': 'option("lower", "upper", "auto", default="auto")',
    'newbie_mode': 'boolean(default=False, help="display commands help")',
    'retry_times': 'integer(default=2, help="connection retry times")',
    'shell': 'boolean(default=True, help="allow to run shell commands")',
    'enable_pager': 'boolean(default=True, help="using pager when output is too tall")',
    'pager': 'string(default=None, help="pager command")',
    'no_info': 'boolean(default=False, help="no `INFO` command sent to server on launch")',
    'bottom_bar': 'boolean(default=True, help="display command hint on bottom bar")',
    'warning': 'boolean(default=True, help="warn against dangerous commands")',
    'prompt': 'string(default="", help="prompt format")',
    'history_location': 'string(default="~/.iredis_history", help="history file location")',
}


class CLIConfig(dict):
    filename = ''


class CLI(command.Command):
    DESC = 'interactive console'

    def set_arguments(self, parser):
        parser.add_argument('-c', '--cmd', default=None, help='command to execute')

        super(CLI, self).set_arguments(parser)

    def run(self, redis_service, cmd):
        cfg = redis_service.plugin_config

        entry.greetings = lambda: None
        config.read_config_file = lambda _: CLIConfig(main=cfg['cli'])

        uri = cfg['uri']
        if not uri:
            login = '{}:{}@'.format(cfg['username'], cfg['password']) if cfg['username'] or cfg['password'] else ''

            if cfg['socket']:
                uri = 'unix://{}{}?db={}'.format(login, cfg['socket'], cfg['db'])
            else:
                uri = 'redis://{}{}:{}/{}'.format(login, cfg['host'], cfg['port'], cfg['db'])

        sys.argv = [
            'nagare db cli',
            '--url',
            uri,
            '--decode',
            cfg['encoding'],
            '--client_name',
            cfg['client_name'],
            '--no-rainbow',
        ] + ([cmd] if cmd else [])

        entry.main()
