
#!/usr/bin/env python
#########################################################################
# main.py								#
#									#
# Command-line utility for interacting with Sensor in SONiC		#
#########################################################################

try:
    import sys
    import os
    import subprocess
    import click
    import imp
    import syslog
    from sonic_device_util import get_machine_info
    from sonic_device_util import get_platform_info
    from syslog_helper import LogHelper
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

VERSION = '1.0'

SYSLOG_IDENTIFIER = "sensorutil"
PLATFORM_SPECIFIC_MODULE_NAME = "sensorutil"
PLATFORM_SPECIFIC_CLASS_NAME = "SensorUtil"
PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
PLATFORM_ROOT_PATH_DOCKER = '/usr/share/sonic/platform'
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
HWSKU_KEY = 'DEVICE_METADATA.localhost.hwsku'
PLATFORM_KEY = 'DEVICE_METADATA.localhost.platform'

# Global platform-specific sensorutil class instance
platform_sensorutil = None



# ==================== Methods for initialization ====================


# Loads platform specific sensorutil module from source
def load_platform_sensorutil():
    global platform_sensorutil

    # Get platform and hwsku
    platform = get_platform_info(get_machine_info())
    if len(platform) != 0:
	platform_path = "/".join([PLATFORM_ROOT_PATH, platform])
    else:
        platform_path = PLATFORM_ROOT_PATH_DOCKER

    # Load platform module from source
    module_file = "/".join([platform_path, "plugins", PLATFORM_SPECIFIC_MODULE_NAME + ".py"])
    if os.path.isfile(module_file):
	module = imp.load_source(PLATFORM_SPECIFIC_MODULE_NAME, module_file)
        try:
            platform_sensorutil_class = getattr(module, PLATFORM_SPECIFIC_CLASS_NAME)
            platform_sensorutil = platform_sensorutil_class()
        except AttributeError, e:
            LogHelper(SYSLOG_IDENTIFIER).log_error("Failed to instantiate '%s' class: %s" % (PLATFORM_SPECIFIC_CLASS_NAME, str(e)), True)
            return -2
    else:
        try:
            from sonic_sensor.sensor_base import SensorBase
            platform_sensorutil = SensorBase()

        except ImportError as e:
	    LogHelper(SYSLOG_IDENTIFIER).log_error(str(e) + "- required module not found")
            raise ImportError(str(e) + "- required module not found")

    return 0


# ==================== CLI commands and groups ====================


# This is our main entrypoint - the main 'sensorutil' command
@click.group()
def cli():
    """sensorutil - Command line utility for providing Sensor Details"""

    if os.geteuid() != 0:
        click.echo("Root privileges are required for this operation")
        sys.exit(1)

    # Load platform-specific psuutil class
    err = load_platform_sensorutil()
    if err != 0 :
	LogHelper(SYSLOG_IDENTIFIER).log_error("Not able to load Platform module")
	raise AttributeError("Not able to load Platform module")


# 'summary' subcommand
@cli.command()
def summary():
	"""Display Sensor Details"""
	try:
		platform_sensorutil.get_data_api()
	except AttributeError:
		LogHelper(SYSLOG_IDENTIFIER).log_error("{} object has no attribute/method {}".format(platform_sensorutil,get_data_api))

if __name__ == '__main__':
    cli()
