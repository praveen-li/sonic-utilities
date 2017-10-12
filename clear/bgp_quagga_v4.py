import click
from clear.main import *


###############################################################################
#
# 'clear ip bgp' cli stanza
#
###############################################################################


@ip.group(cls=AliasedGroup, default_if_no_args=True,
          context_settings=CONTEXT_SETTINGS)
def bgp():
    """Clear BGP (Border Gateway Protocol) peers"""
    pass


# Default 'bgp' command (called if no subcommands or their aliases were passed)
@bgp.command(default=True)
def default():
    """Clear all BGP peers"""
    command = 'sudo vtysh -c "clear ip bgp *"'
    run_command(command)


@bgp.group(cls=AliasedGroup, default_if_no_args=True,
           context_settings=CONTEXT_SETTINGS)
def neighbor():
    pass


@neighbor.command(default=True)
@click.argument('ipaddress', required=False)
def default(ipaddress):
    """Clear BGP neighbors"""
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} "'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp *"'
    run_command(command)


# 'in' subcommand
@neighbor.command('in')
@click.argument('ipaddress', required=False)
def neigh_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} in"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp * in"'
    run_command(command)


# 'out' subcommand
@neighbor.command('out')
@click.argument('ipaddress', required=False)
def neigh_out(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} out"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp * out"'
    run_command(command)


@neighbor.group(cls=AliasedGroup, default_if_no_args=True,
                context_settings=CONTEXT_SETTINGS)
def soft():
    pass


@soft.command(default=True)
@click.argument('ipaddress', required=False)
def default(ipaddress):
    """Clear BGP neighbors soft configuration"""
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} soft "'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp * soft"'
    run_command(command)


# 'soft in' subcommand
@soft.command('in')
@click.argument('ipaddress', required=False)
def soft_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} soft in"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp * soft in"'
    run_command(command)


# 'soft out' subcommand
@soft.command('out')
@click.argument('ipaddress', required=False)
def soft_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear ip bgp {} soft out"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear ip bgp * soft out"'
    run_command(command)
