#! /usr/bin/python -u
# date: 08/09/17

import click
import errno
import os
import subprocess
import sys
from click_default_group import DefaultGroup

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
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
    #click.echo(click.style("Command: ", fg='cyan') + click.style(command, fg='green'))
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    try:
	if pager is True and sys.stdout.isatty():
		click.echo_via_pager(p.stdout.read())
	else:
		click.echo(p.stdout.read())
    except IOError as e:
         # In our version of Click, click.echo() and click.echo_via_pager() do not properly handle
         # SIGPIPE, and if a pipe is broken before all output is processed (e.g., pipe output to 'head'),
        # it will result in a stack trace. This is apparently fixed upstream, but for now, we silently
         # ignore SIGPIPE here.
	if e.errno == errno.EPIPE:
		sys.exit(0)
	else:
		raise


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '-?'])


#
# 'cli' group (root group) ###
#

# THis is our entrypoint - the main "show" command
# TODO: Consider changing function name to 'show' for better understandability
@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def cli():
    """SONiC command line - 'show' command"""
    pass


#
# 'ip' group ###
#

# This allows us to add commands to both cli and ip groups, allowing for
# "show <command>" and "show ip <command>" to function the same
@cli.group()
def ip():
    """Show IP commands"""
    pass


#
# 'interface' group ####
#

# We use the "click.group()" decorator because we want to add this group
# to more than one group, which we do using the "add_command() methods below.
@click.group(cls=AliasedGroup, default_if_no_args=True)
def interface(): # changed name from interfaces to interface
    """Show interface information"""
    pass

# Add 'interfaces' group to both the root 'cli' group and the 'ip' subgroup
cli.add_command(interface)
ip.add_command(interface)


# Default 'interfaces' command (called if no subcommands or their aliases were passed)
@interface.command(default=True)
@click.argument('interfacename', required=False)
def default(interfacename):
    """Show interface status and information"""

    cmd_ifconfig = "/sbin/ifconfig"

    if interfacename is not None:
        command = "{} {}".format(cmd_ifconfig, interfacename)
    else:
        command = cmd_ifconfig
    run_command(command, pager=True)


@interface.group(cls=AliasedGroup, default_if_no_args=True)
def transceiver():
     pass

interface.add_command(transceiver)

@transceiver.command(default=True)
@click.argument('interfacename', required=False)
def default(interfacename):
     if interfacename is not None:
        command = "sudo sfputil -p {}".format(interfacename)
     else:
        command = "sudo sfputil"
     run_command(command)

@transceiver.command()
@click.argument('interfacename', required=True)
def details(interfacename):
	command="sudo sfputil --port {} --dom".format(interfacename)
	run_command(command)

@interface.group(cls=AliasedGroup, default_if_no_args=True)
def statistics():
     pass

interface.add_command(statistics)

@statistics.command(default=True)
@click.argument('interfacename', required=False)
def default(interfacename):
    if interfacename is not None:
        command = "ip -s link show {}".format(interfacename)
    else:
        command='watch -n 5 "sudo portstat -a"'
	os.system(command)
    run_command(command)


@statistics.command()
@click.argument('interfacename', required=False)
def transmitter(interfacename):
   if interfacename is not None:
        command = "ip -s link show {}".format(interfacename)
   else:
        command = "sudo portstat -a | awk -v f=1 -v t=10 '{for(i=f;i<=t;i++) printf(\"%s%s\",$i,(i==t)?\"\\n\":OFS)}'"
   run_command(command)


@statistics.command()
@click.argument('interfacename', required=False)
def receiver(interfacename):
   if interfacename is not None:
        command = "ip -s link show {}".format(interfacename)
   else:
        command="sudo portstat -a | awk '{$4=$5=$6=$7=$8=$9=$10=\"\"; print $0}'"
   run_command(command)


@interface.command()
@click.argument('interfacename', required=False)
def description(interfacename):
     if interfacename is not None:
        command = "sudo vtysh -c 'show interface {}'".format(interfacename)
     else:
        command = "sudo vtysh -c 'show interface description'"
     run_command(command, pager=True)

"""
# 'counters' subcommand
@interface.command()
def counters():
    run_command("sudo portstat -a -p 30", pager=True)
"""

# 'portchannel' subcommand
@interface.command()
def portchannel():
    """Show PortChannel information"""
    run_command("teamshow", pager=True)


@interface.command()
def status():
    """Show Interface status information"""
    run_command("interface_stat", pager=True)

@interface.command()
def portmap():
	"""Show interface port-mapping information"""
	PLATFORM_TEMPLATE_FILE = "/tmp/cli_platform.j2"
	PLATFORM_TEMPLATE_CONTENTS = "Platform: {{ platform }}\n" \
                                 "HwSKU: {{ minigraph_hwsku }}\n" \
                                 "ASIC: {{ asic_type }}"
	f = open(PLATFORM_TEMPLATE_FILE, 'w')
	f.write(PLATFORM_TEMPLATE_CONTENTS)
	f.close()
	command = "sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/sonic_version.yml -t {0}".format(PLATFORM_TEMPLATE_FILE)
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	x = p.stdout.readlines()
	a = x[1][7:]
	command1 = "sudo find / -name {}".format(a)
	p1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE)
	t = p1.stdout.readlines()[0]
	command2 = "cat {}/port_config.ini".format(t.rstrip())
	p2 = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE)
	click.echo(p2.stdout.read())

#
# 'lldp' group ####
#

@cli.group(cls=AliasedGroup, default_if_no_args=False)
def lldp():
    """Show LLDP information"""
    pass

# Default 'lldp' command (called if no subcommands or their aliases were passed)
@lldp.command()
@click.argument('interfacename', required=False)
def neighbors(interfacename):
    """Show LLDP neighbors"""
    if interfacename is not None:
        command = "lldpctl {}".format(interfacename)
        run_command(command)
    else:
        run_command("lldpctl", pager=True)

# 'tables' subcommand ####
@lldp.command()
def table():
    """Show LLDP neighbors in tabular format"""
    run_command("lldpshow", pager=True)

@ip.command()
def protocol():
    """Show IP protocol  information"""
    run_command('sudo vtysh -c "show ip protocol"')


#
# 'bgp' group ####
#

# We use the "click.group()" decorator because we want to add this group
# to more than one group, which we do using the "add_command() methods below.
@click.group(cls=AliasedGroup,default_if_no_args=True)
def bgp():
    """Show BGP (Border Gateway Protocol) information"""
    pass



# Add 'bgp' group to both the root 'cli' group and the 'ip' subgroup
cli.add_command(bgp)
ip.add_command(bgp)



# Default 'bgp' command (called if no subcommands or their aliases were passed)
@bgp.command(default=True)
def default():
    """Show BGP information"""
    run_command('sudo vtysh -c "show ip bgp"')

"""
# 'neighbors' subcommand ####
@bgp.command()
@click.argument('ipaddress', required=False)
def neighbor(ipaddress):
    if ipaddress is not None:
        command = 'sudo vtysh -c "show ip bgp neighbor {} "'.format(ipaddress)
        run_command(command)
    else:
        run_command('sudo vtysh -c "show ip bgp neighbor"', pager=True)
"""

@bgp.group(cls=AliasedGroup, default_if_no_args=True)
def neighbor():
    """Show BGP neighbors"""
    pass

bgp.add_command(neighbor)

@neighbor.command(default=True)
@click.argument('ipaddress', required=False)
def default(ipaddress):
    """Show BGP neighbors"""
    if ipaddress is not None:
        command = 'sudo vtysh -c "show ip bgp neighbor {} "'.format(ipaddress)
        run_command(command)
    else:
        run_command('sudo vtysh -c "show ip bgp neighbor"', pager=True)


# 'advertised-routes' subcommand
@neighbor.command('advertised-routes')
@click.argument('ipaddress')
def advertised_routes(ipaddress):
	command = 'sudo vtysh -c "show ip bgp neighbor {} advertised-routes"'.format(ipaddress)
        run_command(command)

# 'received-routes' subcommand
@neighbor.command('received-routes')
@click.argument('ipaddress')
def received_routes(ipaddress):
        command = 'sudo vtysh -c "show ip bgp neighbor {} received-routes"'.format(ipaddress)
        run_command(command)

# 'routes' subcommand
@neighbor.command('routes')
@click.argument('ipaddress')
def routes(ipaddress):
        command = 'sudo vtysh -c "show ip bgp neighbor {} routes"'.format(ipaddress)
        run_command(command)


# 'summary' subcommand ####
@bgp.command()
def summary():
    """Show summarized information of BGP state"""
    run_command('sudo vtysh -c "show ip bgp summary"')

#########################################
# 'ipv6' group

@cli.group()
def ipv6():
    """Show IPv6 commands"""
    pass

# 'route' command
@ipv6.command()
def route():
    """Show IPv6 route  information"""
    run_command('sudo vtysh -c "show ipv6 route"')

# 'protocol' command
@ipv6.command()
def protocol():
    """Show IPv6 protocol  information"""
    run_command('sudo vtysh -c "show ipv6 protocol"')

# 'bgp' command
@click.group(cls=AliasedGroup,default_if_no_args=True)
def bgp():
    """Show IPv6 BGP (Border Gateway Protocol) information"""
    pass

ipv6.add_command(bgp)


# Default 'bgp' command (called if no subcommands or their aliases were passed)
@bgp.command(default=True)
@click.argument('ipaddress', required=False)
def default(ipaddress):
    """Show IPv6 BGP information"""
    if ipaddress is not None:
	run_command('sudo vtysh -c "show ipv6 bgp {}"'.format(ipaddress))
    else:
	run_command('sudo vtysh -c "show ipv6 bgp"')

# IPV6 BGP 'neighbors' subcommand
@bgp.group(cls=AliasedGroup, default_if_no_args=True)
def neighbors():
    pass

bgp.add_command(neighbors)

@neighbors.command(default=True)
@click.argument('ipaddress')
def default(ipaddress):
    """Show IPv6 BGP neighbors"""
    command = 'sudo vtysh -c "show ipv6 bgp neighbors {} "'.format(ipaddress)
    run_command(command)


# 'advertised-routes' subcommand
@neighbors.command('advertised-routes')
@click.argument('ipaddress')
def advertised_routes(ipaddress):
        command = 'sudo vtysh -c "show ipv6 bgp neighbors {} advertised-routes"'.format(ipaddress)
        run_command(command)

# 'received-routes' subcommand
@neighbors.command('received-routes')
@click.argument('ipaddress')
def received_routes(ipaddress):
        command = 'sudo vtysh -c "show ipv6 bgp neighbors {} received-routes"'.format(ipaddress)
        run_command(command)


# 'routes' subcommand
@neighbors.command('routes')
@click.argument('ipaddress')
def routes(ipaddress):
        command = 'sudo vtysh -c "show ipv6 bgp neighbors {} routes"'.format(ipaddress)
        run_command(command)

# 'IPv6 BGP summary'subcommand
@bgp.command()
def summary():
    """Show summarized information of BGP state"""
    run_command('sudo vtysh -c "show ipv6 bgp summary"')

#
# 'platform' group ####
#

@cli.group(cls=AliasedGroup, default_if_no_args=False)
def platform():
    """Show Platform information"""
    pass

@platform.command()
def summary():
    """Show hardware platform information"""
    click.echo("")

    PLATFORM_TEMPLATE_FILE = "/tmp/cli_platform.j2"
    PLATFORM_TEMPLATE_CONTENTS = "Platform: {{ platform }}\n" \
                                 "HwSKU: {{ minigraph_hwsku }}\n" \
                                 "ASIC: {{ asic_type }}"

    # Create a temporary Jinja2 template file to use with sonic-cfggen
    f = open(PLATFORM_TEMPLATE_FILE, 'w')
    f.write(PLATFORM_TEMPLATE_CONTENTS)
    f.close()

    command = "sonic-cfggen -m /etc/sonic/minigraph.xml -y /etc/sonic/sonic_version.yml -t {0}".format(PLATFORM_TEMPLATE_FILE)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    click.echo(p.stdout.read())

#
# 'hardware' command
#

@cli.command()
def hardware():
     """Show local hardware information"""
     comm="sudo dmidecode -t 1,2,10"
     run_command(comm)

# 'syseeprom' subcommand ####
@platform.command()
def syseeprom():
    """Show system EEPROM information"""
    run_command("decode-syseeprom")


#
# 'logging' group ####
#

@cli.command()
def logging():
	"""Show Logging information"""
        comm = "sudo docker ps --format '{{.Names}}'"
        proc = subprocess.Popen(comm, stdout=subprocess.PIPE, shell=True)
        while True:
                line = proc.stdout.readline()
                if line != '':
                        print(line.rstrip()+'\t'+"docker")
                        print("---------------------------")
                        comm1 = "sudo docker logs {}".format(line.rstrip())
                        proc1 = subprocess.Popen(comm1, stdout=subprocess.PIPE, shell=True)
                        print proc1.stdout.read()
                else:
                        break


#
# 'version' command ###
#

@cli.command()
def version():
    """Show version information"""
    click.echo("")

    VERSION_TEMPLATE_FILE = "/tmp/cli_version.j2"
    VERSION_TEMPLATE_CONTENTS = "SONiC Software Version: SONiC.{{ build_version }}\n" \
                                "Distribution: Debian {{ debian_version }}\n" \
                                "Kernel: {{ kernel_version }}\n" \
                                "Build commit: {{ commit_id }}\n" \
                                "Build date: {{ build_date }}\n" \
                                "Built by: {{ built_by }}"

    # Create a temporary Jinja2 template file to use with sonic-cfggen
    f = open(VERSION_TEMPLATE_FILE, 'w')
    f.write(VERSION_TEMPLATE_CONTENTS)
    f.close()

    command = "sonic-cfggen -y /etc/sonic/sonic_version.yml -t {0}".format(VERSION_TEMPLATE_FILE)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    click.echo(p.stdout.read())

    click.echo("Docker images:")
    command = 'docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}"'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    click.echo(p.stdout.read())


#
# 'environment' command ###
#

@cli.command()
def environment():
    """Show environmentals (voltages, fans, temps)"""
    run_command('sensors', pager=True)

#
# 'processes' group ###
#

@cli.group(cls=AliasedGroup, default_if_no_args=True)
def processes():
    """Show process information"""
    pass


@processes.command(default=True)
def default():
    """Show processes info"""
    # Run top batch mode to prevent unexpected newline after each newline
    run_command('ps -eo pid,ppid,cmd,%mem,%cpu ')

# 'cpu' subcommand
@processes.command()
def cpu():
    """Show processes CPU info"""
    # Run top batch mode to prevent unexpected newline after each newline
    run_command('top -bn 1 -o %CPU', pager=True)

# 'memory' subcommand
@processes.command()
def memory():
    """Show processes memory info"""
    # Run top batch mode to prevent unexpected newline after each newline
    run_command('top -bn 1 -o %MEM', pager=True)

#
# 'users' command ###
#

@cli.command()
def users():
    """Show users"""
    run_command('who')


#
# 'techsupport' command ###
#

@cli.command()
def techsupport():
    """Gather information for troubleshooting"""
    run_command('sudo generate_dump -v')


#
# 'runningconfiguration' group ###
#

@cli.group(cls=AliasedGroup, default_if_no_args=False)
def runningconfiguration():
    """Show current running configuration information"""
    pass


# 'bgp' subcommand
@runningconfiguration.command()
def bgp():
    """Show BGP running configuration"""
    run_command('sudo vtysh -c "show running-config"', pager=True)


# 'interfaces' subcommand
@runningconfiguration.command()
@click.argument('interfacename', required=False)
def interfaces(interfacename):
    """Show Interfaces running configuration"""
    if interfacename is not None:
        command = "cat /etc/network/interfaces | grep {} -A 4".format(interfacename)
        run_command(command)
    else:
        run_command('cat /etc/network/interfaces', pager=True)

# 'snmp' subcommand
@runningconfiguration.command()
@click.argument('server', required=False)
def snmp(server):
    """Show SNMP information"""
    if server is not None:
	command = 'docker exec -it snmp cat /etc/snmp/snmpd.conf | grep -i agentAddress'
    else:
	command = 'docker exec -it snmp cat /etc/snmp/snmpd.conf'
    run_command(command, pager=True)

cli.add_command(snmp)

# 'ntp' subcommand
@runningconfiguration.command()
def ntp():
    """Show NTP running configuration"""
    run_command('cat /etc/ntp.conf', pager=True)


# 'startupconfiguration' group ###
#

@cli.group(cls=AliasedGroup, default_if_no_args=False)
def startupconfiguration():
    """Show startup configuration information"""
    pass


# 'bgp' subcommand
@startupconfiguration.command()
def bgp():
    """Show BGP startup configuration"""
    run_command('docker exec -it bgp cat /etc/quagga/bgpd.conf')

#
# 'arp' command ####
#

@click.command()
@click.argument('ipaddress', required=False)
def arp(ipaddress):
    """Show IP arp table"""
    cmd = "/usr/sbin/arp"
    if ipaddress is not None:
        command = '{} {}'.format(cmd, ipaddress)
        run_command(command)
    else:
        run_command(cmd, pager=True)

# Add 'arp' command to both the root 'cli' group and the 'ip' subgroup
cli.add_command(arp)
ip.add_command(arp)


#
# 'route' command ####
#

@click.command()
@click.argument('ipaddress', required=False)
def route(ipaddress):
    """Show IP routing table"""
    if ipaddress is not None:
        command = 'sudo vtysh -c "show ip route {}"'.format(ipaddress)
        run_command(command)
    else:
        run_command('sudo vtysh -c "show ip route"', pager=True)

# Add 'route' command to both the root 'cli' group and the 'ip' subgroup
cli.add_command(route)
ip.add_command(route)


#
# 'ntp' command ####
#

@cli.command()
def ntp():
    """Show NTP information"""
    run_command('ntpq -p')


#
# 'uptime' command ####
#

@cli.command()
def uptime():
    """Show system uptime"""
    run_command('uptime -p')

@cli.command()
def clock():
    """Show date and time"""
    run_command('date')

@cli.command('system-memory')
def system_memory():
    """Show memory information"""
    comm="free -m"
    run_command(comm)

@cli.command('services')
def services():
    """Show all daemon services"""
    comm = "sudo docker ps --format '{{.Names}}'"
    proc = subprocess.Popen(comm, stdout=subprocess.PIPE, shell=True)
    while True:
	line = proc.stdout.readline()
	if line != '':
		print(line.rstrip()+'\t'+"docker")
		print("---------------------------")
		comm1 = "sudo docker exec -it {} ps -ef | sed '$d'".format(line.rstrip())
		proc1 = subprocess.Popen(comm1, stdout=subprocess.PIPE, shell=True)
		print proc1.stdout.read()
	else:
		break
@cli.group(cls=AliasedGroup, default_if_no_args=True)
def acl():
    """Show ACL information"""
    pass


@acl.command(default=True)
def default():
    """Show ACL info"""
    run_command('aclshow')

@acl.command()
def v4():
    """Show ACL for v4 information"""
    comm="aclshow -t dataacl"
    run_command(comm)

@acl.command()
def v6():
    """Show ACL for v6 information"""
    comm="aclshow -t data-aclv6"
    run_command(comm)


if __name__ == '__main__':
    cli()
