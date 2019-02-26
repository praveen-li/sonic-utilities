#!/bin/bash

#
# Author: Zhenggen Xu (zxu@linkedin.com)
# This script is used to print, list and set the hwskus under the same platform.
# Regular user can print and list the current hwsku and all available hwskus.
# To change the hwsku, you will need root access. The main idea of the script
# was that each hwsku reserves it's own portmaping, minigraph, json etc. When we change the hwsku,
# the script will pickup the right configuration files and reboot the box to take effect
# (script will ask for reboot confirmation). This will override the existing configuration.
# The following command line help should explain the syntax
#
display_help() {
    echo "Usage: $0 [-h] [-p] [-l] [-s HWSKU]" >&2
    echo
    echo "   -h, --help           print this usage page"
    echo "   -p, --print          print the current HWSKU"
    echo "   -l, --list           list the available HWSKUs"
    echo "   -s, --set            set the HWSKU"
    exit 0
}

HWSKU_ROOT='/usr/share/sonic/device/'
platform=`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`
current_hwsku=`sonic-cfggen -d -v DEVICE_METADATA.localhost.hwsku`
RUNNING_PATH='/etc/sonic/'

config_hwsku_exec() {
    config_hwsku=$1
    while true; do
        read -p "This will reset to the initial configuration with the port mode specified and restart all services. [Y/N] " yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* ) echo "No changes were made"; exit;;
            * ) echo "Please answer yes or no.";;
        esac
    done

    printf -v hwsku_minigraph "%s%s%s%s%s" $HWSKU_ROOT $platform '/' $config_hwsku '/' "minigraph.xml"
    target_minigraph=$RUNNING_PATH
    target_minigraph+="minigraph.xml"

    #echo copy $hwsku_minigraph " to "  $target_minigraph
    cp $hwsku_minigraph $target_minigraph

    #load minigraph
    echo "loading the new configuration"
    config load_minigraph -y

    # save the json after backup
    echo "backup the old config_db.json to .bak file and save the new one."
    target_json=$RUNNING_PATH
    target_json+="config_db.json"
    backup_json=$target_json".bak"
    #echo copy $target_json to $backup_json
    cp $target_json $backup_json

    config save -y
}

check_supported_hwskus() {
    # Check the available HWSKUs
    platform_dir="$HWSKU_ROOT""$platform"/
    supported_hwskus=`ls -l $platform_dir | egrep '^d' | awk '{print $9}' | grep -v plugins | grep -v led-code`
}
config_hwsku_fun() {

    config_hwsku=$1
    # Check root privileges
    if [ "$EUID" -ne 0 ]
    then
      echo "Please run as root"
      exit
    fi

    if [ "$config_hwsku" == "$current_hwsku" ]; then
        echo "The HWSKU configured is current, no changes were made"
        exit
    fi


    # Check the available HWSKUs
    check_supported_hwskus

    for hwsku in $supported_hwskus
    do
	if [ $config_hwsku == $hwsku ]; then
	    config_hwsku_exec "$config_hwsku"
	    exit
	fi
    done

    # Not matching any HWSKU names, print error
    printf "Please use one of the options:\n"
    printf "%s\n" $supported_hwskus
    exit 1
}

main() {
    case "$1" in
    -h | --help)
        display_help
        ;;
    -p | --print)
        echo $current_hwsku
        ;;
    -l | --list)
        check_supported_hwskus
        printf "%s\n" $supported_hwskus
        ;;
    -s | --set)
        config_hwsku=$2
        config_hwsku_fun "$config_hwsku"
        ;;
    *)
        echo "Please use options as following:" >&2
        display_help
        ;;
    esac
}

main "$@"
