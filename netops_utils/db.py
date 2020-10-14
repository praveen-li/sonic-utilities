from swsssdk import ConfigDBConnector

'''
    These file contains libraries exposed to network operation teams to interact
    with DB. Right now we expose only get functions. As per need we can expose
    Subscriber functions as well.
'''

class DbCommon(ConfigDBConnector):
    def __init__(self, **kwargs):
        super(DbCommon, self).__init__(**kwargs)
        return

    '''
        Exposed functions are: connect, get_all_tables, get_keys(), get_table()
        and get_entry(). Also get_< specific >_table() functions are written
        for few DBs.
    '''
    def connect(self, wait_for_init=False, retry_on=False):
        self.db_connect(self.dbname, wait_for_init, retry_on)

    def get_all_tables(self):
        return self.get_config()

    '''
        Override all functions which should not be exposed.
    '''
    def delete_table(self, table):
        pass
    def delete(self, db_name, key, *args, **kwargs):
        pass
    def delete_all_by_pattern(self, db_name, pattern, *args, **kwargs):
        pass
    def delete(self, db_id, key):
        pass
    def delete_all_by_pattern(self, db_id, pattern):
        pass
    def exists(self, db_name, key):
        pass
    def exists(self, db_id, key):
        pass
    def keys(self, db_name, pattern='*', *args, **kwargs):
        pass
    def keys(self, db_id):
        pass
    def _subscribe_keyspace_notification(self, db_id):
        pass
    def _unsubscribe_keyspace_notification(self, db_id):
        pass
    def listen(self):
        pass
    def mod_config(self, data):
        pass
    def mod_entry(self, table, key, data):
        pass
    def publish(self, db_name, channel, message):
        pass
    def publish(self, db_id, channel, message):
        pass
    def set_entry(self, table, key, data):
        pass
    def set(self, db_name, _hash, key, val, *args, **kwargs):
        pass
    def set(self, db_id, _hash, key, val):
        pass
    def set_entry(self, table, key, data):
        pass
    def subscribe(self, table, handler):
        pass
    def unsubscribe(self, table):
        pass
    def _subscribe_keyspace_notification(self, db_id):
        pass
    def _unsubscribe_keyspace_notification(self, db_id):
        pass
    def unsubscribe(self, table):
        pass
    def _unsubscribe_keyspace_notification(self, db_id):
        pass
    def get_all(self, db_name, _hash, *args, **kwargs):
        pass
    def get_all(self, db_id, _hash):
        pass
    # end of class DbCommon

class AppDb(DbCommon):
    def __init__(self, **kwargs):
        super(AppDb, self).__init__(**kwargs)
        self.TABLE_NAME_SEPARATOR = ':'
        self.KEY_SEPARATOR = ':'
        self.dbname = "APPL_DB"
        return

    def get_neigh_table(self):
        return self.get_table('NEIGH_TABLE')

    def get_route_table(self):
        return self.get_table('ROUTE_TABLE')

    def get_sflow_table(self):
        return self.get_table('sflow_table')

    def get_sflow_session_table(self):
        return self.get_table('sflow_session_table')

    def get_port_table(self):
        return self.get_table('port_table')

    def get_copp_table(self):
        return self.get_table('copp_table')

    def get_lldp_entry_table(self):
        return self.get_table('lldp_entry_table')

    def get_intf_table(self):
        return self.get_table('intf_table')

    # end of class AppDb

class ConfigDb(DbCommon):
    def __init__(self, **kwargs):
        super(ConfigDb, self).__init__(**kwargs)
        self.TABLE_NAME_SEPARATOR = '|'
        self.KEY_SEPARATOR = '|'
        self.dbname = "CONFIG_DB"
        return

    def get_port_table(self):
        return self.get_table('PORT')

    def get_interface_table(self):
        return self.get_table('INTERFACE')

    # end of class ConfigDb

class CounterDb(DbCommon):
    def __init__(self, **kwargs):
        super(CounterDb, self).__init__(**kwargs)
        self.TABLE_NAME_SEPARATOR = ':'
        self.KEY_SEPARATOR = ':'
        self.dbname = "COUNTERS_DB"
        return

    def get_counters_table(self):
        return self.get_table('COUNTERS')

    # end of class CounterDb

class FlexCountDb(DbCommon):
    def __init__(self, **kwargs):
        super(FlexCountDb, self).__init__(**kwargs)
        self.TABLE_NAME_SEPARATOR = ':'
        self.KEY_SEPARATOR = ':'
        self.dbname = "FLEX_COUNTER_DB"
        return

    def get_flex_counter_table(self):
        return self.get_table('FLEX_COUNTER_TABLE')

    # end of class FlexCountDb

class StateDb(DbCommon):
    def __init__(self, **kwargs):
        super(StateDb, self).__init__(**kwargs)
        self.TABLE_NAME_SEPARATOR = '|'
        self.KEY_SEPARATOR = '|'
        self.dbname = "STATE_DB"
        return

    def get_warm_restart_table(self):
        return self.get_table('warm_restart_table')

    def get_port_table(self):
        return self.get_table('port_table')

    def get_interface_table(self):
        return self.get_table('interface_table')

    # end of class StateDb

'''
    Make SonicDb Singleton, so that one process can not have multiple connections
    with DB, this is to restrict too many connections to Redis DB.
    Note: Multiple processes can still have multiple instance of this class.
'''
class Singleton(object):
    def __new__(cls):
        if cls.__dict__.get("__instance__") is not None:
            return cls.__instance__

        cls.__instance__ = object.__new__(cls)
        cls.__instance__.init()
        return cls.__instance__

    def __init__(self):
        pass

class SonicDb(Singleton):
    def init(self):
        #print("Init SonicDb")
        self.cfgdb = ConfigDb()
        self.cfgdb.connect()

        self.appldb = AppDb()
        self.appldb.connect()

        self.countdb = CounterDb()
        self.countdb.connect()

        self.flexcountdb = FlexCountDb()
        self.flexcountdb.connect()

        self.statedb = StateDb()
        self.statedb.connect()
