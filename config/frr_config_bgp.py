import click
import re
from config.main import *

##########################################################################
# This file contains bgp group of config command for FRR Routing stack.  #
##########################################################################

# Helper function 'config bgp ...' command
def _frr_get_asn_from_ip_neighbour(ipaddr, verbose=False):
    """
    Get Local ASN for given ip address. Caller must verify
    that ipaddr is our BGP neighbor.
    :param ipaddr: ip address of neighbor
    :return: Local ASN for BGP neighbor else Exception
    """
    vtyshCmd = "'show bgp neighbor {}'".format(ipaddr)
    command = 'sudo vtysh -c {} | grep "local AS"'.format(vtyshCmd)
    (out, err) = run_command(command, display_cmd=verbose, ignore_error=True, return_output=True)
    if err:
	print("Error: While searching for Local ASN of neighbor {}".format(ipaddr))
	raise click.Abort

    try:
        localAsn = re.search(r"^.*local AS (.+?),.*$", out).group(1)
        localAsnI = int(localAsn)
        if verbose:
            print("local ASN for neighbor {} is {}".format(ipaddr, localAsn))
    except Exception as e:
        print("Error: BGP information not found for Neighbor {}".format(ipaddr))
        if verbose:
            print("Exception:{}".format(e))
        raise click.Abort

    return localAsn

def _frr_change_bgp_session_status(ipaddr, status, verbose):
    """
    Bring up/down BGP session with neighbor.
    :param ipaddr: ip address of neighbor.
    :param status: up or down.
    :param verbose: Verbosity True or False.
    :return: None
    """
    # Convert ip to lowercase to match with output of vtysh commands
    ipaddr_lower = ipaddr.lower()

    # Get Local ASN for Neighbour
    asn = _frr_get_asn_from_ip_neighbour(ipaddr_lower, verbose)

    if status == 'down':
        vtyshCmd = "'configure terminal' -c 'router bgp {}'".format(asn)
        vtyshCmd = vtyshCmd + " -c 'neighbor {} shutdown'".format(ipaddr_lower)
        command = "sudo vtysh -c {}".format(vtyshCmd)
        run_command(command=command, display_cmd=verbose, ignore_error=False)
    elif status == 'up':
        vtyshCmd = "'configure terminal' -c 'router bgp {}'".format(asn)
        vtyshCmd = vtyshCmd + " -c 'no neighbor {} shutdown'".format(ipaddr_lower)
        command = "sudo vtysh -c {}".format(vtyshCmd)
        run_command(command=command, display_cmd=verbose, ignore_error=False)

    return

#
# 'bgp' group
#
@config.group()
def bgp():
    """BGP-related configuration tasks"""
    pass

#
# 'shutdown' subgroup
#

@bgp.group()
def shutdown():
    """Shut down BGP session(s)"""
    pass

# 'all' subcommand
@shutdown.command()
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
def all(verbose):
    """Shutdown BGP session for all neighbors"""
    print("NO-OP Command for Sonic FRR")

# 'neighbor' subcommand
@shutdown.command()
@click.argument('ipaddr', metavar='<ipaddr>', required=True)
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
def neighbor(ipaddr, verbose):
    """Shut down BGP session by neighbor IP address"""
    _frr_change_bgp_session_status(ipaddr, 'down', verbose)

@bgp.group()
def startup():
    """Start up BGP session(s)"""
    pass

# 'all' subcommand
@startup.command()
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
def all(verbose):
    """Start up BGP session for all neighbors"""
    print("NO-OP Command for Sonic FRR")

# 'neighbor' subcommand
@startup.command()
@click.argument('ipaddr', metavar='<ipaddr>', required=True)
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output")
def neighbor(ipaddr, verbose):
    """Start up BGP session by neighbor IP address"""
    _frr_change_bgp_session_status(ipaddr, 'up', verbose)
