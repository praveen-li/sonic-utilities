import click
from show.main import *


###############################################################################
#
# 'show ip bgp' cli stanza
#
###############################################################################


@ip.group(cls=AliasedGroup, default_if_no_args=False)
def bgp():
    """Show IPv4 BGP (Border Gateway Protocol) information"""
    pass


# 'summary' subcommand ("show ip bgp summary")
@bgp.command()
def summary():
    """Show summarized information of IPv4 BGP state"""
    run_command('sudo vtysh -c "show ip bgp summary"')


# 'neighbors' subcommand ("show ip bgp neighbors")
@bgp.command()
@click.argument('ipaddress', required=False)
@click.argument('info_type', type=click.Choice(['routes', 'advertised-routes', 'received-routes']), required=False)
def neighbors(ipaddress, info_type):
    """Show IP (IPv4) BGP neighbors"""

    command = 'sudo vtysh -c "show ip bgp neighbor'

    if ipaddress is not None:
        command += ' {}'.format(ipaddress)

        # info_type is only valid if ipaddress is specified
        if info_type is not None:
            command += ' {}'.format(info_type)

    command += '"'

    run_command(command)
