# config_mgmt.py
# Provides a class for configuration validation and for Dynamic Port Breakout.

try:

    import re
    import syslog

    from json import load
    from os import system
    from time import sleep as tsleep
    from imp import load_source

    # SONiC specific imports
    import sonic_yang
    from swsssdk import ConfigDBConnector, SonicV2Connector, port_util

    # Using load_source to 'import /usr/local/bin/sonic-cfggen as sonic_cfggen'
    # since /usr/local/bin/sonic-cfggen does not have .py extension.
    load_source('sonic_cfggen', '/usr/local/bin/sonic-cfggen')
    from sonic_cfggen import deep_update, FormatConverter, sort_data

except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

# Globals
# This class may not need to know about YANG_DIR ?, sonic_yang shd use
# default dir.
YANG_DIR = "/usr/local/yang-models"
CONFIG_DB_JSON_FILE = '/etc/sonic/confib_db.json'
# TODO: Find a place for it on sonic switch.
DEFAULT_CONFIG_DB_JSON_FILE = '/etc/sonic/default_config_db.json'

# Class to handle config managment for SONIC, this class will use PLY to verify
# config for the commands which are capable of change in config DB.

class ConfigMgmt():

    def __init__(self, source="configDB", debug=False, allowTablesWithoutYang=True):

        try:
            self.configdbJsonIn = None
            self.configdbJsonOut = None
            self.allowTablesWithoutYang = allowTablesWithoutYang

            # logging vars
            self.SYSLOG_IDENTIFIER = "ConfigMgmt"
            self.DEBUG = debug

            self.sy = sonic_yang.SonicYang(YANG_DIR, debug=debug)
            # load yang models
            self.sy.loadYangModel()
            # load jIn from config DB or from config DB json file.
            if source.lower() == 'configdb':
                self.readConfigDB()
            # treat any other source as file input
            else:
                self.readConfigDBJson(source)
            # this will crop config, xlate and load.
            self.sy.loadData(self.configdbJsonIn)

            # Raise if tables without YANG models are not allowed but exist.
            if not allowTablesWithoutYang and len(self.sy.tablesWithOutYang):
                raise Exception('Config has tables without YANG models')

        except Exception as e:
            print(e)
            raise(Exception('ConfigMgmt Class creation failed'))

        return

    def __del__(self):
        pass

    """
    Return tables loaded in config for which YANG model does not exist.
    """
    def tablesWithoutYang(self):

        return self.sy.tablesWithOutYang

    """
    Explicit function to load config data in Yang Data Tree
    """
    def loadData(self, configdbJson):
        self.sy.loadData(configdbJson)
        # Raise if tables without YANG models are not allowed but exist.
        if not self.allowTablesWithoutYang and len(self.sy.tablesWithOutYang):
            raise Exception('Config has tables without YANG models')

        return

    """
    Validate current Data Tree
    """
    def validateConfigData(self):

        try:
            self.sy.validate_data_tree()
        except Exception as e:
            self.sysLog(msg='Data Validation Failed')
            return False

        print('Data Validation successful')
        self.sysLog(msg='Data Validation successful')
        return True

    """
    syslog Support
    """
    def sysLog(self, debug=syslog.LOG_INFO, msg=None):

        # log debug only if enabled
        if self.DEBUG == False and debug == syslog.LOG_DEBUG:
            return
        syslog.openlog(self.SYSLOG_IDENTIFIER)
        syslog.syslog(debug, msg)
        syslog.closelog()

        return

    def readConfigDBJson(self, source=CONFIG_DB_JSON_FILE):

        print('Reading data from {}'.format(source))
        self.configdbJsonIn = readJsonFile(source)
        #print(type(self.configdbJsonIn))
        if not self.configdbJsonIn:
            raise(Exception("Can not load config from config DB json file"))
        self.sysLog(msg='Reading Input {}'.format(self.configdbJsonIn))

        return

    """
        Get config from redis config DB
    """
    def readConfigDB(self):

        print('Reading data from Redis configDb')

        # Read from config DB on sonic switch
        db_kwargs = dict(); data = dict()
        configdb = ConfigDBConnector(**db_kwargs)
        configdb.connect()
        deep_update(data, FormatConverter.db_to_output(configdb.get_config()))
        self.configdbJsonIn =  FormatConverter.to_serialized(data)
        self.sysLog(syslog.LOG_DEBUG, 'Reading Input from ConfigDB {}'.\
            format(self.configdbJsonIn))

        return

    def writeConfigDB(self, jDiff):
        print('Writing in Config DB')
        """
        On Sonic Switch
        """
        db_kwargs = dict(); data = dict()
        configdb = ConfigDBConnector(**db_kwargs)
        configdb.connect(False)
        deep_update(data, FormatConverter.to_deserialized(jDiff))
        data = sort_data(data)
        self.sysLog(msg="Write in DB: {}".format(data))
        configdb.mod_config(FormatConverter.output_to_db(data))

        return

# End of Class ConfigMgmt

"""
    Config MGMT class for Dynamic Port Breakout(DPB).
    This is derived from ConfigMgmt.
"""
class ConfigMgmtDPB(ConfigMgmt):

    def __init__(self, source="configDB", debug=False, allowTablesWithoutYang=True):

        try:
            ConfigMgmt.__init__(self, source=source, debug=debug, \
                allowTablesWithoutYang=allowTablesWithoutYang)
            self.oidKey = 'ASIC_STATE:SAI_OBJECT_TYPE_PORT:oid:0x'

        except Exception as e:
            print(e)
            raise(Exception('ConfigMgmtDPB Class creation failed'))

        return

    def __del__(self):
        pass

    """
      Check if a key exists in ASIC DB or not.
    """
    def _checkKeyinAsicDB(self, key, db):

        self.sysLog(msg='Check Key in Asic DB: {}'.format(key))
        try:
            # chk key in ASIC DB
            if db.exists('ASIC_DB', key):
                return True
        except Exception as e:
            print(e)
            raise(e)

        return False

    def _testRedisCli(self, key):
        # To Debug
        if self.DEBUG:
            cmd = 'sudo redis-cli -n 1 hgetall "{}"'.format(key)
            self.sysLog(syslog.LOG_DEBUG, "Running {}".format(cmd))
            print(cmd)
            system(cmd)
        return

    """
     Check ASIC DB for PORTs in port List
     ports: List of ports
     portMap: port to OID map.
     Return: True, if all ports are not present.
    """
    def _checkNoPortsInAsicDb(self, db, ports, portMap):
        try:
            # connect to ASIC DB,
            db.connect(db.ASIC_DB)
            for port in ports:
                key = self.oidKey + portMap[port]
                if self._checkKeyinAsicDB(key, db) == False:
                    # Test again via redis-cli
                    self._testRedisCli(key)
                else:
                    return False

        except Exception as e:
            print(e)
            return False

        return True

    """
    Verify in the Asic DB that port are deleted,
    Keep on trying till timeout period.
    db = database, ports, portMap, timeout
    """
    def _verifyAsicDB(self, db, ports, portMap, timeout):

        print("Verify Port Deletion from Asic DB, Wait...")
        self.sysLog(msg="Verify Port Deletion from Asic DB, Wait...")

        try:
            for waitTime in range(timeout):
                self.sysLog(msg='Check Asic DB: {} try'.format(waitTime+1))
                # checkNoPortsInAsicDb will return True if all ports are not
                # present in ASIC DB
                if self._checkNoPortsInAsicDb(db, ports, portMap):
                    break
                tsleep(1)

            # raise if timer expired
            if waitTime + 1 == timeout:
                print("!!!  Critical Failure, Ports are not Deleted from \
                    ASIC DB, Bail Out  !!!")
                self.sysLog(syslog.LOG_CRIT, "!!!  Critical Failure, Ports \
                    are not Deleted from ASIC DB, Bail Out  !!!")
                raise(Exception("Ports are present in ASIC DB after timeout"))

        except Exception as e:
            print(e)
            raise e

        return True

    def breakOutPort(self, delPorts=list(), addPorts= list(), portJson=dict(), \
        force=False, loadDefConfig=True):

        MAX_WAIT = 60
        try:
            # delete Port and get the Config diff, deps and True/False
            delConfigToLoad, deps, ret = self._deletePorts(ports=delPorts, \
                force=force)
            # return dependencies if delete port fails
            if ret == False:
                return deps, ret

            # add Ports and get the config diff and True/False
            addConfigtoLoad, ret = self._addPorts(ports=addPorts, \
                portJson=portJson, loadDefConfig=loadDefConfig)
            # return if ret is False, Great thing, no change is done in Config
            if ret == False:
                return None, ret

            # Save Port OIDs Mapping Before Deleting Port
            dataBase = SonicV2Connector(host="127.0.0.1")
            if_name_map, if_oid_map = port_util.get_interface_oid_map(dataBase)
            self.sysLog(syslog.LOG_DEBUG, 'if_name_map {}'.format(if_name_map))

            # If we are here, then get ready to update the Config DB, Update
            # deletion of Config first, then verify in Asic DB for port deletion,
            # then update addition of ports in config DB.
            self.writeConfigDB(delConfigToLoad)
            # Verify in Asic DB,
            self._verifyAsicDB(db=dataBase, ports=delPorts, portMap=if_name_map, \
                timeout=MAX_WAIT)
            self.writeConfigDB(addConfigtoLoad)

        except Exception as e:
            print(e)
            return None, False

        return None, True

    """
    Delete all ports.
    delPorts: list of port names.
    force: if false return dependecies, else delete dependencies.

    Return:
    WithOut Force: (xpath of dependecies, False) or (None, True)
    With Force: (xpath of dependecies, False) or (None, True)
    """
    def _deletePorts(self, ports=list(), force=False):

        configToLoad = None; deps = None
        try:
            self.sysLog(msg="delPorts ports:{} force:{}".format(ports, force))

            print('\nStart Port Deletion')
            deps = list()

            # Get all dependecies for ports
            for port in ports:
                xPathPort = self.sy.findXpathPortLeaf(port)
                print('Find dependecies for port {}'.format(port))
                self.sysLog(msg='Find dependecies for port {}'.format(port))
                # print("Generated Xpath:" + xPathPort)
                dep = self.sy.find_data_dependencies(str(xPathPort))
                if dep:
                    deps.extend(dep)

            # No further action with no force and deps exist
            if force == False and deps:
                return configToLoad, deps, False;

            # delets all deps, No topological sort is needed as of now, if deletion
            # of deps fails, return immediately
            elif deps and force:
                for dep in deps:
                    self.sysLog(msg='Deleting {}'.format(dep))
                    self.sy.deleteNode(str(dep))
            # mark deps as None now,
            deps = None

            # all deps are deleted now, delete all ports now
            for port in ports:
                xPathPort = self.sy.findXpathPort(port)
                print("Deleting Port: " + port)
                self.sysLog(msg='Deleting Port:{}'.format(port))
                self.sy.deleteNode(str(xPathPort))

            # Let`s Validate the tree now
            if self.validateConfigData()==False:
                return configToLoad, deps, False;

            # All great if we are here, Lets get the diff
            self.configdbJsonOut = self.sy.getData()
            # Update configToLoad
            configToLoad = self._updateDiffConfigDB()

        except Exception as e:
            print(e)
            print("Port Deletion Failed")
            return configToLoad, deps, False

        return configToLoad, deps, True

    """
    Add Ports and default config for ports to config DB, after validation of
    data tree

    PortJson: Config DB Json Part of all Ports same as PORT Table of Config DB.
    ports = list of ports
    loadDefConfig: If loadDefConfig add default config as well.

    return: Sucess: True or Failure: False
    """
    def _addPorts(self, ports=list(), portJson=dict(), loadDefConfig=True):

        configToLoad = None
        try:
            self.sysLog(msg='Start Port Addition')
            self.sysLog(msg="addPorts ports:{} loadDefConfig:{}".\
                format(ports, loadDefConfig))
            self.sysLog(msg="addPorts Args portjson {}".format(portJson))

            print('\nStart Port Addition')

            if loadDefConfig:
                defConfig = self._getDefaultConfig(ports)
                self.sysLog(msg='Default Config: {}'.format(defConfig))

            # get the latest Data Tree, save this in input config, since this
            # is our starting point now
            self.configdbJsonIn = self.sy.getData()

            # Get the out dict as well, if not done already
            if self.configdbJsonOut is None:
                self.configdbJsonOut = self.sy.getData()

            # update portJson in configdbJsonOut PORT part
            self.configdbJsonOut['PORT'].update(portJson['PORT'])
            # merge new config with data tree, this is json level merge.
            # We do not allow new table merge while adding default config.
            if loadDefConfig:
                print("Merge Default Config for {}".format(ports))
                self.sysLog(msg="Merge Default Config for {}".format(ports))
                self._mergeConfigs(self.configdbJsonOut, defConfig, True)

            # create a tree with merged config and validate, if validation is
            # sucessful, then configdbJsonOut contains final and valid config.
            self.sy.loadData(self.configdbJsonOut)
            if self.validateConfigData()==False:
                return configToLoad, False

            # All great if we are here, Let`s get the diff and update COnfig
            configToLoad = self._updateDiffConfigDB()

        except Exception as e:
            print(e)
            print("Port Addition Failed")
            return configToLoad, False

        return configToLoad, True

    """
    Merge second dict in first, Note both first and second dict will be changed
    First Dict will have merged part D1 + D2
    Second dict will have D2 - D1 [unique keys in D2]
    Unique keys in D2 will be merged in D1 only if uniqueKeys=True
    """
    def _mergeConfigs(self, D1, D2, uniqueKeys=True):

        try:
            def _mergeItems(it1, it2):
                if isinstance(it1, list) and isinstance(it2, list):
                    it1.extend(it2)
                elif isinstance(it1, dict) and isinstance(it2, dict):
                    self._mergeConfigs(it1, it2)
                elif isinstance(it1, list) or isinstance(it2, list):
                    raise ("Can not merge Configs, List problem")
                elif isinstance(it1, dict) or isinstance(it2, dict):
                    raise ("Can not merge Configs, Dict problem")
                else:
                    #print("Do nothing")
                    # First Dict takes priority
                    pass
                return

            for it in D1.keys():
                #print(it)
                # D2 has the key
                if D2.get(it):
                    _mergeItems(D1[it], D2[it])
                    del D2[it]
                # D2  does not have the keys
                else:
                    pass

            # if uniqueKeys are needed, merge rest of the keys of D2 in D1
            if uniqueKeys:
                D1.update(D2)
        except Exce as e:
            print("Merge Config failed")
            print(e)
            raise e

        return D1

    """
    search Relevant Keys in Config using DFS, This function is mainly
    used to search port related config in Default ConfigDbJson file.
    In: Config to be searched
    skeys: Keys to be searched in In Config i.e. search Keys.
    Out: Contains the search result
    """
    def _searchKeysInConfig(self, In, Out, skeys):

        found = False
        if isinstance(In, dict):
            for key in In.keys():
                #print("key:" + key)
                for skey in skeys:
                    # pattern is very specific to current primary keys in
                    # config DB, may need to be updated later.
                    pattern = '^' + skey + '\|' + '|' + skey + '$' + \
                        '|' + '^' + skey + '$'
                    #print(pattern)
                    reg = re.compile(pattern)
                    #print(reg)
                    if reg.search(key):
                        # In primary key, only 1 match can be found, so return
                        # print("Added key:" + key)
                        Out[key] = In[key]
                        found = True
                        break
                # Put the key in Out by default, if not added already.
                # Remove later, if subelements does not contain any port.
                if Out.get(key) is None:
                    Out[key] = type(In[key])()
                    if self._searchKeysInConfig(In[key], Out[key], skeys) == False:
                        del Out[key]
                    else:
                        found = True

        elif isinstance(In, list):
            for skey in skeys:
                if skey in In:
                    found = True
                    Out.append(skey)
                    #print("Added in list:" + port)

        else:
            # nothing for other keys
            pass

        return found

    """
    This function returns the relavant keys in Input Config.
    For Example: All Ports related Config in Config DB.
    """
    def configWithKeys(self, configIn=dict(), keys=list()):

        configOut = dict()
        try:
            if len(configIn) and len(keys):
                self._searchKeysInConfig(configIn, configOut, skeys=keys)
        except Exception as e:
            print("configWithKeys Failed, Error: {}".format(str(e)))
            raise e

        return configOut

    """
    Create a defConfig for given Ports from Default Config File.
    """
    def _getDefaultConfig(self, ports=list()):

        # function code
        try:
            print("Generating default config for {}".format(ports))
            defConfigIn = readJsonFile(DEFAULT_CONFIG_DB_JSON_FILE)
            #print(defConfigIn)
            defConfigOut = dict()
            self._searchKeysInConfig(defConfigIn, defConfigOut, skeys=ports)
        except Exception as e:
            print("getDefaultConfig Failed, Error: {}".format(str(e)))
            raise e

        return defConfigOut

    def _updateDiffConfigDB(self):

        try:
            # Get the Diff
            print('Generate Final Config to write in DB')
            configDBdiff = self._diffJson()
            # Process diff and create Config which can be updated in Config DB
            configToLoad = self._createConfigToLoad(configDBdiff, \
                self.configdbJsonIn, self.configdbJsonOut)

        except Exception as e:
            print("Config Diff Generation failed")
            print(e)
            raise e

        return configToLoad

    """
    Create the config to write in Config DB from json diff
    diff: diff in input config and output config.
    inp: input config before delete/add ports.
    outp: output config after delete/add ports.
    """
    def _createConfigToLoad(self, diff, inp, outp):

        ### Internal Functions ###
        """
        Handle deletes in diff dict
        """
        def _deleteHandler(diff, inp, outp, config):

            # if output is dict, delete keys from config
            if isinstance(inp, dict):
                for key in diff:
                    #print(key)
                    # make sure keys from diff are present in inp but not in outp
                    # then delete it.
                    if key in inp and key not in outp:
                        # assign key to None(null), redis will delete entire key
                        config[key] = None
                    else:
                        # log such keys
                        print("Diff: Probably wrong key: {}".format(key))

            elif isinstance(inp, list):
                # just take list from output
                # print("Delete from List: {} {} {}".format(inp, outp, list))
                #print(type(config))
                config.extend(outp)

            return

        """
        Handle inserts in diff dict
        """
        def _insertHandler(diff, inp, outp, config):

            # if outp is a dict
            if isinstance(outp, dict):
                for key in diff:
                    #print(key)
                    # make sure keys are only in outp
                    if key not in inp and key in outp:
                        # assign key in config same as outp
                        config[key] = outp[key]
                    else:
                        # log such keys
                        print("Diff: Probably wrong key: {}".format(key))

            elif isinstance(outp, list):
                # just take list from output
                # print("Delete from List: {} {} {}".format(inp, outp, list))
                config.extend(outp)

            return

        """
        Recursively iterate diff to generate config to write in configDB
        """
        def _recurCreateConfig(diff, inp, outp, config):

            changed = False
            # updates are represented by list in diff and as dict in outp\inp
            # we do not allow updates right now
            if isinstance(diff, list) and isinstance(outp, dict):
                return changed

            idx = -1
            for key in diff:
                #print(key)
                idx = idx + 1
                if str(key) == '$delete':
                    _deleteHandler(diff[key], inp, outp, config)
                    changed = True
                elif str(key) == '$insert':
                    _insertHandler(diff[key], inp, outp, config)
                    changed = True
                else:
                    # insert in config by default, remove later if not needed
                    if isinstance(diff, dict):
                        # config should match with outp
                        config[key] = type(outp[key])()
                        if _recurCreateConfig(diff[key], inp[key], outp[key], \
                            config[key]) == False:
                            del config[key]
                        else:
                            changed = True
                    elif isinstance(diff, list):
                        config.append(key)
                        if _recurCreateConfig(diff[idx], inp[idx], outp[idx], \
                            config[-1]) == False:
                            del config[-1]
                        else:
                            changed = True

            return changed

        ### Function Code ###
        try:
            configToLoad = dict()
            #import pdb; pdb.set_trace()
            _recurCreateConfig(diff, inp, outp, configToLoad)

        except Exception as e:
            print("Create Config to load in DB, Failed")
            print(e)
            raise e

        return configToLoad

    def _diffJson(self):

        from jsondiff import diff
        return diff(self.configdbJsonIn, self.configdbJsonOut, syntax='symmetric')

# end of class ConfigMgmtDPB

# Helper Functions
def readJsonFile(fileName):

    try:
        with open(fileName) as f:
            result = load(f)
    except Exception as e:
        raise Exception(e)

    return result
