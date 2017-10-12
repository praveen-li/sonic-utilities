import click
from clear.main import *


###############################################################################
#
# 'clear bgp ipv6' cli stanza
#
###############################################################################


@bgp.group(cls=AliasedGroup, default_if_no_args=True)
def ipv6():
    """Clear BGP IPv6 peers / state"""
    pass


# Default 'bgp' command (called if no subcommands or their aliases were passed)
@ipv6.command(default=True)
def default():
    """Clear all BGP peers"""
    command = 'sudo vtysh -c "clear bgp ipv6 *"'
    run_command(command)


@ipv6.group(cls=AliasedGroup, default_if_no_args=True,
            context_settings=CONTEXT_SETTINGS)
def neighbor():
    pass


@neighbor.command(default=True)
@click.argument('ipaddress', required=False)
def default(ipaddress):
    """Clear BGP neighbors"""
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear bgp ipv6 {} "'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 *"'
    run_command(command)


# 'in' subcommand
@neighbor.command('in')
@click.argument('ipaddress', required=False)
def neigh_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear bgp ipv6 {} in"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 * in"'
    run_command(command)


# 'out' subcommand
@neighbor.command('out')
@click.argument('ipaddress', required=False)
def neigh_out(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear bgp ipv6 {} out"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 * out"'
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
        command = 'sudo vtysh -c "clear bgp ipv6 {} soft "'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 * soft"'
    run_command(command)


# 'soft in' subcommand
@soft.command('in')
@click.argument('ipaddress', required=False)
def soft_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear bgp ipv6 {} soft in"'.format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 * soft in"'
    run_command(command)


# 'soft out' subcommand
@soft.command('out')
@click.argument('ipaddress', required=False)
def soft_in(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "clear bgp ipv6 {} soft out"' \
            .format(ipaddress)
    else:
        command = 'sudo vtysh -c "clear bgp ipv6 * soft out"'
    run_command(command)
