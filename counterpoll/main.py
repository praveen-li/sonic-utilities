#! /usr/bin/python -u

import click
import swsssdk
from tabulate import tabulate

@click.group()
def cli():
    """ SONiC Static Counter Poll configurations """

# Queue counter commands
@cli.group()
def queue():
    """ Queue counter commands """

@queue.command()
@click.argument('poll_interval', type=click.IntRange(100, 30000))
def interval(poll_interval):
    """ Set queue counter query interval """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    queue_info = {}
    if poll_interval is not None:
        queue_info['POLL_INTERVAL'] = poll_interval
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE", queue_info)

@queue.command()
def enable():
    """ Enable queue counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    queue_info = {}
    queue_info['FLEX_COUNTER_STATUS'] = 'enable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE", queue_info)

@queue.command()
def disable():
    """ Disable queue counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    queue_info = {}
    queue_info['FLEX_COUNTER_STATUS'] = 'disable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE", queue_info)

# Port counter commands
@cli.group()
def port():
    """ Queue counter commands """

@port.command()
@click.argument('poll_interval', type=click.IntRange(100, 30000))
def interval(poll_interval):
    """ Set queue counter query interval """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    port_info = {}
    if poll_interval is not None:
        port_info['POLL_INTERVAL'] = poll_interval
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PORT", port_info)

@port.command()
def enable():
    """ Enable port counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    port_info = {}
    port_info['FLEX_COUNTER_STATUS'] = 'enable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PORT", port_info)

@port.command()
def disable():
    """ Disable port counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    port_info = {}
    port_info['FLEX_COUNTER_STATUS'] = 'disable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PORT", port_info)

# Watermark counter commands
@cli.group()
def watermark():
    """ Watermark counter commands """

@watermark.command()
@click.argument('poll_interval', type=click.IntRange(1000, 30000))
def interval(poll_interval):
    """ Set watermark counter query interval for both queue and PG watermarks """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    queue_wm_info = {}
    pg_wm_info = {}
    if poll_interval is not None:
        queue_wm_info['POLL_INTERVAL'] = poll_interval
        pg_wm_info['POLL_INTERVAL'] = poll_interval
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE_WATERMARK", queue_wm_info)
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PG_WATERMARK", pg_wm_info)

@watermark.command()
def enable():
    """ Enable watermark counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    fc_info = {}
    fc_info['FLEX_COUNTER_STATUS'] = 'enable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE_WATERMARK", fc_info)
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PG_WATERMARK", fc_info)

@watermark.command()
def disable():
    """ Disable watermark counter query """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    fc_info = {}
    fc_info['FLEX_COUNTER_STATUS'] = 'disable'
    configdb.mod_entry("FLEX_COUNTER_TABLE", "QUEUE_WATERMARK", fc_info)
    configdb.mod_entry("FLEX_COUNTER_TABLE", "PG_WATERMARK", fc_info)

@cli.command()
def show():
    """ Show the counter configuration """
    configdb = swsssdk.ConfigDBConnector()
    configdb.connect()
    queue_info = configdb.get_entry('FLEX_COUNTER_TABLE', 'QUEUE')
    port_info = configdb.get_entry('FLEX_COUNTER_TABLE', 'PORT')
    queue_wm_info = configdb.get_entry('FLEX_COUNTER_TABLE', 'QUEUE_WATERMARK')
    pg_wm_info = configdb.get_entry('FLEX_COUNTER_TABLE', 'PG_WATERMARK')
    
    header = ("Type", "Interval (in ms)", "Status")
    data = []
    if queue_info:
        data.append(["QUEUE_STAT", queue_info["POLL_INTERVAL"] if 'POLL_INTERVAL' in queue_info else 'default (10000)', queue_info["FLEX_COUNTER_STATUS"] if 'FLEX_COUNTER_STATUS' in queue_info else 'disable' ])
    if port_info:
        data.append(["PORT_STAT", port_info["POLL_INTERVAL"] if 'POLL_INTERVAL' in port_info else 'default (1000)', port_info["FLEX_COUNTER_STATUS"] if 'FLEX_COUNTER_STATUS' in port_info else 'disable'])
    if queue_wm_info:
        data.append(["QUEUE_WATERMARK_STAT", queue_wm_info["POLL_INTERVAL"] if 'POLL_INTERVAL' in queue_wm_info else 'default (10000)', queue_wm_info["FLEX_COUNTER_STATUS"] if 'FLEX_COUNTER_STATUS' in queue_wm_info else 'disable' ])
    if pg_wm_info:
        data.append(["PG_WATERMARK_STAT", pg_wm_info["POLL_INTERVAL"] if 'POLL_INTERVAL' in pg_wm_info else 'default (10000)', pg_wm_info["FLEX_COUNTER_STATUS"] if 'FLEX_COUNTER_STATUS' in pg_wm_info else 'disable'])

    print tabulate(data, headers=header, tablefmt="simple", missingval="")

