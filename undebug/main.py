import click
import os
import subprocess
from click_default_group import DefaultGroup
from sonic_device_util import get_system_routing_stack

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


# This is from the aliases example:
# https://github.com/pallets/click/blob/57c6f09611fc47ca80db0bd010f05998b3c0aa95/examples/aliases/aliases.py
class Config(object):
    """Object to hold CLI config"""

    def __init__(self):
        self.path = os.getcwd()
        self.aliases = {}

    def read_config(self, filename):
        parser = configparser.RawConfigParser()
        parser.read([filename])
        try:
            self.aliases.update(parser.items('aliases'))
        except configparser.NoSectionError:
            pass


# Global Config object
_config = None


# This aliased group has been modified from click examples to inherit from DefaultGroup instead of click.Group.
# DefaultFroup is a superclass of click.Group which calls a default subcommand instead of showing
# a help message if no subcommand is passed
class AliasedGroup(DefaultGroup):
    """This subclass of a DefaultGroup supports looking up aliases in a config
    file and with a bit of magic.
    """

    def get_command(self, ctx, cmd_name):
        global _config

        # If we haven't instantiated our global config, do it now and load current config
        if _config is None:
            _config = Config()

            # Load our config file
            cfg_file = os.path.join(os.path.dirname(__file__), 'aliases.ini')
            _config.read_config(cfg_file)

        # Try to get builtin commands as normal
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # No builtin found. Look up an explicit command alias in the config
        if cmd_name in _config.aliases:
            actual_cmd = _config.aliases[cmd_name]
            return click.Group.get_command(self, ctx, actual_cmd)

        # Alternative option: if we did not find an explicit alias we
        # allow automatic abbreviation of the command.  "status" for
        # instance will match "st".  We only allow that however if
        # there is only one command.
        matches = [x for x in self.list_commands(ctx)
                   if x.lower().startswith(cmd_name.lower())]
        if not matches:
            # No command name matched. Issue Default command.
            ctx.arg0 = cmd_name
            cmd_name = self.default_cmd_name
            return DefaultGroup.get_command(self, ctx, cmd_name)
        elif len(matches) == 1:
            return DefaultGroup.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def run_command(command, pager=False):
    if pager is True:
        click.echo(click.style("Command: ", fg='cyan') + click.style(command, fg='green'))
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        click.echo_via_pager(p.stdout.read())
    else:
        click.echo(click.style("Command: ", fg='cyan') + click.style(command, fg='green'))
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        click.echo(p.stdout.read())


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '-?'])


#
# 'cli' group (root group) ###
#

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def cli():
    """SONiC undebugging commands for routing events"""
    pass

#
# Inserting 'undebug' functionality into cli's parse-chain. Undebugging commands
# are determined by the routing-stack being elected.
#
routing_stack = get_system_routing_stack()

if routing_stack == "quagga":

    from .undebug_quagga import bgp
    cli.add_command(bgp)
    from .undebug_quagga import zebra
    cli.add_command(zebra)

elif routing_stack == "frr":

    @cli.command()
    @click.argument('debug_args', nargs = -1, required = False)
    def bgp(debug_args):
        """Debug BGP information"""
        debug_cmd = "no debug bgp"
        for arg in debug_args:
            debug_cmd += " " + str(arg)
        command = 'sudo vtysh -c "{}"'.format(debug_cmd)
        run_command(command)

    @cli.command()
    @click.argument('debug_args', nargs = -1, required = False)
    def zebra(debug_args):
        """Debug Zebra information"""
        debug_cmd = "no debug zebra"
        for arg in debug_args:
            debug_cmd += " " + str(arg)
        command = 'sudo vtysh -c "{}"'.format(debug_cmd)
        run_command(command)


if __name__ == '__main__':
    cli()
