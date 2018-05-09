import click
from undebug.main import *


###############################################################################
#
# 'undebug bgp' cli stanza
#
###############################################################################


@cli.group(cls=AliasedGroup, default_if_no_args=False)
def bgp():
    """undebug bgp events """
    pass

@bgp.command()
def as4():
    """undebug bgp AS4 actions """
    command = 'sudo vtysh -c "no debug bgp as4"'
    run_command(command)

@bgp.command()
def events():
    """undebug bgp events """
    command = 'sudo vtysh -c "no debug bgp events"'
    run_command(command)

@bgp.command()
def filters():
    """undebug bgp filters """
    command = 'sudo vtysh -c "no debug bgp filters"'
    run_command(command)

@bgp.command()
def fsm():
    """undebug bgp fsm """
    command = 'sudo vtysh -c "no debug bgp fsm"'
    run_command(command)

@bgp.command()
def keepalives():
    """undebug bgp keepalives """
    command = 'sudo vtysh -c "no debug bgp keepalives"'
    run_command(command)

@bgp.command()
def updates():
    """undebug bgp updates """
    command = 'sudo vtysh -c "no debug bgp updates"'
    run_command(command)

@bgp.command()
def zebra():
    """undebug bgp zebra messages """
    command = 'sudo vtysh -c "no debug bgp zebra"'
    run_command(command)


###############################################################################
#
# 'undebug zebra' cli stanza
#
###############################################################################


@cli.group(cls=AliasedGroup, default_if_no_args=False)
def zebra():
    """undebug zebra events """
    pass

@zebra.command()
def events():
    """undebug zebra events """
    command = 'sudo vtysh -c "no debug zebra events"'
    run_command(command)

@zebra.command()
def fpm():
    """undebug zebra fpm events """
    command = 'sudo vtysh -c "no debug zebra fpm"'
    run_command(command)

@zebra.command()
def kernel():
    """undebug zebra's kernel-interface events """
    command = 'sudo vtysh -c "no debug zebra kernel"'
    run_command(command)

@zebra.command()
def packet():
    """undebug zebra packets """
    command = 'sudo vtysh -c "no debug zebra packet"'
    run_command(command)

@zebra.command()
def rib():
    """undebug zebra RIB events """
    command = 'sudo vtysh -c "no debug zebra rib"'
    run_command(command)
