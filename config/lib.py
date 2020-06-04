import os

from swsssdk import ConfigDBConnector

VLAN_SUB_INTERFACE_SEPARATOR = '.'

def get_interface_naming_mode():
    mode = os.getenv('SONIC_CLI_IFACE_MODE')
    if mode is None:
        mode = "default"
    return mode

def interface_alias_to_name(interface_alias):
    """Return default interface name if alias name is given as argument
    """
    config_db = ConfigDBConnector()
    config_db.connect()
    port_dict = config_db.get_table('PORT')

    vlan_id = ""
    sub_intf_sep_idx = -1
    if interface_alias is not None:
        sub_intf_sep_idx = interface_alias.find(VLAN_SUB_INTERFACE_SEPARATOR)
        if sub_intf_sep_idx != -1:
            vlan_id = interface_alias[sub_intf_sep_idx + 1:]
            # interface_alias holds the parent port name so the subsequent logic still applies
            interface_alias = interface_alias[:sub_intf_sep_idx]

    if interface_alias is not None:
        if not port_dict:
            click.echo("port_dict is None!")
            raise click.Abort()
        for port_name in port_dict.keys():
            if interface_alias == port_dict[port_name]['alias']:
                return port_name if sub_intf_sep_idx == -1 else port_name + VLAN_SUB_INTERFACE_SEPARATOR + vlan_id

    # Interface alias not in port_dict, just return interface_alias, e.g.,
    # portchannel is passed in as argument, which does not have an alias
    return interface_alias if sub_intf_sep_idx == -1 else interface_alias + VLAN_SUB_INTERFACE_SEPARATOR + vlan_id

def interface_name_is_valid(interface_name):
    """Check if the interface name is valid
    """
    config_db = ConfigDBConnector()
    config_db.connect()
    port_dict = config_db.get_table('PORT')
    port_channel_dict = config_db.get_table('PORTCHANNEL')
    sub_port_intf_dict = config_db.get_table('VLAN_SUB_INTERFACE')

    if get_interface_naming_mode() == "alias":
        interface_name = interface_alias_to_name(interface_name)

    if interface_name is not None:
        if not port_dict:
            click.echo("port_dict is None!")
            raise click.Abort()
        for port_name in port_dict.keys():
            if interface_name == port_name:
                return True
        if port_channel_dict:
            for port_channel_name in port_channel_dict.keys():
                if interface_name == port_channel_name:
                    return True
        if sub_port_intf_dict:
            for sub_port_intf_name in sub_port_intf_dict.keys():
                if interface_name == sub_port_intf_name:
                    return True
    return False

