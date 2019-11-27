#!/usr/bin/env python
#
# config_mgmt.py
# Provides a class for configuration validation and for Dynamic Port Breakout.

try:
    #from swsssdk import ConfigDBConnector
    from pprint import PrettyPrinter, pprint
    from json import dump, load, dumps, loads
    from sys import path as sysPath
    from os import path as osPath
    # import custom
    sysPath.append(osPath.relpath("../../sonic-yang-mgmt/"))
    from sonic_yang import *
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

# Read given JSON file
def readJsonFile(fileName):
    #print(fileName)
    try:
        with open(fileName) as f:
            result = load(f)
    except Exception as e:
        raise Exception(e)

    return result

# print pretty
prt = PrettyPrinter(indent=4)
def prtprint(obj):
    prt.pprint(obj)
    return

# Class to handle config managment for SONIC, this class will use PLY to verify
# config for the commands which are capable of change in config DB.

class configMgmt():

    def __init__(self, source="configDBJson"):

        self.configdbJsonIn = None
        self.configdbJsonOut = None

        # load jIn from config DB or from config DB json file. Call
        # readConfigDBJson for it or call _readConfigDB.
        source = source.lower()
        if source == 'configdbjson':
            self.readConfigDBJson()
        elif source == 'configdb':
            self.readConfigDB()
        else:
            print("Wrong source for config")
            exit(1)

        YANG_DIR = "../../sonic-yang-mgmt/yang-models"
        self.sy = sonic_yang(YANG_DIR)
        # load yang models
        self.sy.loadYangModel()
        # this will crop config, xlate and load.
        self.sy.load_data(self.configdbJsonIn)

        return

    def readConfigDBJson(self):

        # TODO: match it with /etc/sonic/config_db.json
        CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/lca1-ta1-asw0_config_db.json"
        self.configdbJsonIn = readJsonFile(CONFIG_DB_JSON_FILE)
        #print(type(self.configdbJsonIn))
        if not self.configdbJsonIn:
            print("Can not load config from config DB json file")

        return

    """
        Get config from redis config DB
    """
    def readConfigDB(self):

        # We have to rad similar to sonic-cfggen due to merging of keys
        # configdb = ConfigDBConnector(**db_kwargs)
        # configdb.connect()
        # deep_update(data, FormatConverter.db_to_output(configdb.get_config()))
        # json.dumps(FormatConverter.to_serialized(data)

        #CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/redis_config_db.json"
        CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/redis_config_db_addCase.json"
        self.configdbJsonIn = readJsonFile(CONFIG_DB_JSON_FILE)
        #print(type(self.configdbJsonIn))
        if not self.configdbJsonIn:
            print("Can not load config from config DB json file")


        return

    """
    Delete all ports.
    delPorts: list of port names.
    force: if false return dependecies, else delete dependencies.

    Return:
    WithOut Force: (xpath of dependecies, False) or (None, True)
    With Force: (xpath of dependecies, False) or (None, True)
    """
    def deletePorts(self, delPorts=list(), force=False):

        print(f.__name__)

        try:
            deps = list()

            # Get all dependecies for ports
            for port in delPorts:
                xPathPort = self.sy.findXpathPortLeaf(port)
                print("Generated Xpath:" + xPathPort)
                xPathPort = "/sonic-port:sonic-port/PORT/PORT_LIST[port_name='Ethernet0']/port_name"
                dep = self.sy.find_data_dependencies(str(xPathPort))
                if dep:
                    #print(dep)
                    deps.extend(dep)

            print(deps)
            # No further action with no force and deps exist
            if force == False and deps:
                return deps, False;

            # delets all deps, No topological sort is needed as of now, if deletion
            # of deps fails, return immediately
            elif deps and force:
                for dep in deps:
                    print(dep)
                    if self.sy.delete_node(str(dep)) == False:
                        print("Port Deletion failed for {}".format(dep))
                        return deps, False

            # all deps are deleted now, delete all ports now
            for port in delPorts:
                xPathPort = self.sy.findXpathPort(port)
                print("xPathPort: " + xPathPort)
                if self.sy.delete_node(str(xPathPort)) == False:
                    print("Deletion failed for {}".format(xPathPort))
                    return xPathPort, False

            # Let`s Validate the tree now
            if self.validateConfigData()==False:
                return None, False

            # All great if we are here, Lets get the diff and update Config
            self.configdbJsonOut = self.sy.get_data()
            if self.writeConfigDB()==False:
                return _, False

        except Exception as e:
            print("Port Deletion Failed")
            print(e)
            return None, False

        return None, True

    """
    Add Ports to config DB, after validation of data tree
    addPortJson: Config DB Json Part of all Ports same as PORT Table of Config DB.
    force: If Force add default config as well.

    return: Sucess: True or Failure: False
    """
    def addPorts(self, addPorts=list(), portJson=dict(), force=False):

        try:
            # get default config if forced
            #if force:
            #    defConfig = self.getDefaultConfig(addPorts)

            defConfig = {
                "VLAN": {
                    "Vlan100": {
                        "members": [
                            "Ethernet0",
                            "Ethernet2"
                            ]
                        }
                    },
                "ACL_TABLE": {
                    "NO-NSW-PACL-V4": {
                        "ports": [
                            "Ethernet0",
                            "Ethernet2"
                            ]
                        },
                    "NO-NSW-PACL-V6": {
                        "ports": [
                            "Ethernet0",
                            "Ethernet2"
                            ]
                        },
                    },
                "INTERFACE": {
                    "Ethernet2|2a04:f547:6222:2002::2/126": {
                        "scope": "global",
                        "family": "IPv6"
                        },
                    },
                "VLAN_MEMBER": {
                    "Vlan100|Ethernet0": {
                        "tagging_mode": "untagged"
                    },
                }
            }

            # Merge PortJson and default config
            portJson.update(defConfig)
            defConfig = None
            prtprint(portJson)

            # get the latest Data Tree, save this in input config, since this
            # is our starting point now
            self.configdbJsonIn = self.sy.get_data()

            # Get the out dict as well, if not done already
            if self.configdbJsonOut is None:
                self.configdbJsonOut = self.sy.get_data()

            # merge new config with data tree, json level
            self.mergeConfigs(self.configdbJsonOut, portJson)
            # create a tree with merged config and validate, if validation is
            # sucessful, then configdbJsonOut contains final and valid config.
            self.sy.load_data(self.configdbJsonOut)
            if self.validateConfigData()==False:
                return False

            # All great if we are here, Let`s get the diff and update COnfig
            self.writeConfigDB()

        except Exception as e:
            print("Port Addition Failed")
            return False

        return True

    # merge 2 configs in 1, both are dict
    def mergeConfigs(self, D1, D2):

        try:
            #print(" Merge Config")
            #import pdb; pdb.set_trace()

            def mergeItems(it1, it2):
                if isinstance(it1, list) and isinstance(it2, list):
                    it1.extend(it2)
                elif isinstance(it1, dict) and isinstance(it2, dict):
                    self.mergeConfigs(it1, it2)
                elif isinstance(it1, list) or isinstance(it2, list):
                    raise ("Can not merge Configs, List problem")
                elif isinstance(it1, dict) or isinstance(it2, dict):
                    raise ("Can not merge Configs, Dict problem")
                else:
                    print("Do nothing")
                    # First Dict takes priority
                    pass
                return

            for it in D1.keys():
                #print(it)
                # D2 has the key
                if D2.get(it):
                    mergeItems(D1[it], D2[it])
                    del D2[it]
                # D2  does not have the keys
                else:
                    pass

            # merge rest of the keys in D1
            D1.update(D2)
        except Exce as e:
            print("Merge Config failed")
            print(e)
            raise e

        return D1

    def getDefaultConfig(self, add_Ports=list()):

        CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/redis_config_db.json"
        print("Get Default config")
        # get schemda depedencies on PORT
        xpath = "/sonic-port:sonic-port/sonic-port:PORT/sonic-port:PORT_LIST/sonic-port:port_name"
        deps = self.sy.find_schema_dependencies(xpath)
        print(deps)

    def validateConfigData(self):

        if self.sy.validate_data_tree()==False:
            print("Data Velidation Failed")
            return False
        return True

    def writeConfigDB(self):

        # Get the Diff
        configDBdiff = self.diffJson()
        #prtprint(configDBdiff)
        # Update Config DB:
        return

    def diffJson(self):

        from jsondiff import diff
        return diff(self.configdbJsonIn, self.configdbJsonOut, syntax='symmetric')

# end of config_mgmt class

def testRun_Config_Reload_load():
    print('Test Run Config Reload')
    cm = configMgmt('configDBJson')

    # Validate
    valid = cm.validateConfigData()
    print("Data is valid: {}".format(valid))

    return

def testRun_Delete_Ports():
    print('Test Run Delete Ports')
    cm = configMgmt('configDBjson')
    # Validate
    valid = cm.validateConfigData()
    print("Data is valid: {}".format(valid))

    deps, ret = cm.deletePorts(delPorts=['Ethernet0'], force=True)
    if ret == False:
        print("Port Deletion Test failed")
        return

    return

# Test fo Add Ports
def testRun_Add_Ports():
    print('Test Run Add Ports')
    cm = configMgmt('configDB')
    # Validate
    valid = cm.validateConfigData()
    print("Data is valid: {}".format(valid))

    portJson = {
        "PORT": {
            "Ethernet0": {
                    "alias": "Eth1/1",
                    "admin_status": "up",
                    "lanes": "65, 66",
                    "description": "",
                    "speed": "50000"
            },
            "Ethernet2": {
                    "alias": "Eth1/3",
                    "admin_status": "up",
                    "lanes": "67, 68",
                    "description": "",
                    "speed": "50000"
            }
        }
    }

    cm.addPorts(addPorts=['Ethernet0', 'Ethernet2'], portJson=portJson, force=True)

    return

def test_sonic_yang():

        # CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/yang_orig/sonic_config_data.json"
        CONFIG_DB_JSON_FILE = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/lca1-ta1-asw0_config_db.json"

        #YANG_DIR = "../../sonic-yang-mgmt/tests/yang-model-tests/custom_code/yang_orig"
        YANG_DIR = "../../sonic-yang-mgmt/yang-models"

        sy = sonic_yang(YANG_DIR)
        # load yang models
        #sy.load_schema_modules(YANG_DIR)
        sy.loadYangModel()

        #sy.load_data(CONFIG_DB_JSON_FILE)
        # this will crop config, xlate and load.
        sy.load_data(readJsonFile(CONFIG_DB_JSON_FILE))

        #xPathPort = "/sonic-vlan:PORT/PORT_LIST[port_name='Ethernet0']/port_name"
        xPathPort = "/sonic-port:sonic-port/PORT/PORT_LIST[port_name='Ethernet0']/port_name"

        print("xpath: " + xPathPort)
        dep = sy.find_data_dependencies(xPathPort)
        for d in dep:
            print(d)


if __name__ == '__main__':
    #testRun_Config_Reload_load()
    testRun_Delete_Ports()
    #testRun_Add_Ports()
    #test_sonic_yang()
