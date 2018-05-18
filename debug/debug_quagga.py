import click
from debug.main import *


###############################################################################
#
# 'debug bgp' cli stanza
#
###############################################################################


@cli.group(cls=AliasedGroup, default_if_no_args=False)
def bgp():
    """debug bgp events """
    pass

@bgp.command()
def as4():
    """debug bgp AS4 actions """
    command = 'sudo vtysh -c "debug bgp as4"'
    run_command(command)

@bgp.command()
def events():
    """debug bgp events """
    command = 'sudo vtysh -c "debug bgp events"'
    run_command(command)

@bgp.command()
def filters():
    """debug bgp filters """
    command = 'sudo vtysh -c "debug bgp filters"'
    run_command(command)

@bgp.command()
def fsm():
    """debug bgp fsm """
    command = 'sudo vtysh -c "debug bgp fsm"'
    run_command(command)

@bgp.command()
def keepalives():
    """debug bgp keepalives """
    command = 'sudo vtysh -c "debug bgp keepalives"'
    run_command(command)

@bgp.command()
def updates():
    """debug bgp updates """
    command = 'sudo vtysh -c "debug bgp updates"'
    run_command(command)

@bgp.command()
def zebra():
    """debug bgp zebra messages """
    command = 'sudo vtysh -c "debug bgp zebra"'
    run_command(command)


###############################################################################
#
# 'debug zebra' cli stanza
#
###############################################################################


@cli.group(cls=AliasedGroup, default_if_no_args=False)
def zebra():
    """debug zebra events """
    pass

@zebra.command()
def events():
    """debug zebra events """
    command = 'sudo vtysh -c "debug zebra events"'
    run_command(command)

@zebra.command()
def fpm():
    """debug zebra fpm events """
    command = 'sudo vtysh -c "debug zebra fpm"'
    run_command(command)

@zebra.command()
def kernel():
    """debug zebra's kernel-interface events """
    command = 'sudo vtysh -c "debug zebra kernel"'
    run_command(command)

@zebra.command()
def packet():
    """debug zebra packets """
    command = 'sudo vtysh -c "debug zebra packet"'
    run_command(command)

@zebra.command()
def rib():
    """debug zebra RIB events """
    command = 'sudo vtysh -c "debug zebra rib"'
    run_command(command)
