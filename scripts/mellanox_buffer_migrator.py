from sonic_py_common import logger

SYSLOG_IDENTIFIER = 'mellanox_buffer_migrator'

# Global logger instance
log = logger.Logger(SYSLOG_IDENTIFIER)

class MellanoxBufferMigrator():
    def __init__(self, configDB):
        self.configDB = configDB

    mellanox_default_parameter = {
        "version_1_0_2": {
            # Buffer pool migration control info
            "pool_configuration_list": ["spc1_t0_pool", "spc1_t1_pool", "spc2_t0_pool", "spc2_t1_pool"],

            # Buffer pool configuration info
            "buffer_pool_list" : ['ingress_lossless_pool', 'egress_lossless_pool', 'ingress_lossy_pool', 'egress_lossy_pool'],
            "spc1_t0_pool": {"ingress_lossless_pool": { "size": "4194304", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "7340032", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "16777152", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "7340032", "type": "egress", "mode": "dynamic" } },
            "spc1_t1_pool": {"ingress_lossless_pool": { "size": "2097152", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "5242880", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "16777152", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "5242880", "type": "egress", "mode": "dynamic" } },
            "spc2_t0_pool": {"ingress_lossless_pool": { "size": "8224768", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "8224768", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "35966016", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "8224768", "type": "egress", "mode": "dynamic" } },
            "spc2_t1_pool": {"ingress_lossless_pool": { "size": "12042240", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "12042240", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "35966016", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "12042240", "type": "egress", "mode": "dynamic" } },
        },
        "version_1_0_3": {
            # On Mellanox platform the buffer pool size changed since
            # version with new SDK 4.3.3052, SONiC to SONiC update
            # from version with old SDK will be broken without migration.
            #
            "pool_configuration_list": ["spc1_t0_pool", "spc1_t1_pool", "spc2_t0_pool", "spc2_t1_pool", "spc2_3800_t0_pool", "spc2_3800_t1_pool"],

            # Buffer pool configuration info
            "buffer_pool_list" : ['ingress_lossless_pool', 'egress_lossless_pool', 'ingress_lossy_pool', 'egress_lossy_pool'],
            "spc1_t0_pool": {"ingress_lossless_pool": { "size": "5029836", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "5029836", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "14024599", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "5029836", "type": "egress", "mode": "dynamic" } },
            "spc1_t1_pool": {"ingress_lossless_pool": { "size": "2097100", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "2097100", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "14024599", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "2097100", "type": "egress", "mode": "dynamic" } },

            "spc2_t0_pool": {"ingress_lossless_pool": { "size": "14983147", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "14983147", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "34340822", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "14983147", "type": "egress", "mode": "dynamic" } },
            "spc2_t1_pool": {"ingress_lossless_pool": { "size": "9158635", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "9158635", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "34340822", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "9158635", "type": "egress", "mode": "dynamic" } },

            # 3800 platform has gearbox installed so the buffer pool size is different with other Spectrum2 platform
            "spc2_3800_t0_pool": {"ingress_lossless_pool": { "size": "28196784", "type": "ingress", "mode": "dynamic" },
                                  "ingress_lossy_pool": { "size": "28196784", "type": "ingress", "mode": "dynamic" },
                                  "egress_lossless_pool": { "size": "34340832", "type": "egress", "mode": "dynamic" },
                                  "egress_lossy_pool": {"size": "28196784", "type": "egress", "mode": "dynamic" } },
            "spc2_3800_t1_pool": {"ingress_lossless_pool": { "size": "17891280", "type": "ingress", "mode": "dynamic" },
                                  "ingress_lossy_pool": { "size": "17891280", "type": "ingress", "mode": "dynamic" },
                                  "egress_lossless_pool": { "size": "34340832", "type": "egress", "mode": "dynamic" },
                                  "egress_lossy_pool": {"size": "17891280", "type": "egress", "mode": "dynamic" } },

            # Lossless headroom info
            "spc1_headroom": {"pg_lossless_10000_5m_profile": {"size": "34816", "xon": "18432"},
                              "pg_lossless_25000_5m_profile": {"size": "34816", "xon": "18432"},
                              "pg_lossless_40000_5m_profile": {"size": "34816", "xon": "18432"},
                              "pg_lossless_50000_5m_profile": {"size": "34816", "xon": "18432"},
                              "pg_lossless_100000_5m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_10000_40m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_25000_40m_profile": {"size": "39936", "xon": "18432"},
                              "pg_lossless_40000_40m_profile": {"size": "41984", "xon": "18432"},
                              "pg_lossless_50000_40m_profile": {"size": "41984", "xon": "18432"},
                              "pg_lossless_100000_40m_profile": {"size": "54272", "xon": "18432"},
                              "pg_lossless_10000_300m_profile": {"size": "49152", "xon": "18432"},
                              "pg_lossless_25000_300m_profile": {"size": "71680", "xon": "18432"},
                              "pg_lossless_40000_300m_profile": {"size": "94208", "xon": "18432"},
                              "pg_lossless_50000_300m_profile": {"size": "94208", "xon": "18432"},
                              "pg_lossless_100000_300m_profile": {"size": "184320", "xon": "18432"}},
            "spc2_headroom": {"pg_lossless_1000_5m_profile": {"size": "35840", "xon": "18432"},
                              "pg_lossless_10000_5m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_25000_5m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_40000_5m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_50000_5m_profile": {"size": "37888", "xon": "18432"},
                              "pg_lossless_100000_5m_profile": {"size": "38912", "xon": "18432"},
                              "pg_lossless_200000_5m_profile": {"size": "41984", "xon": "18432"},
                              "pg_lossless_1000_40m_profile": {"size": "36864", "xon": "18432"},
                              "pg_lossless_10000_40m_profile": {"size": "38912", "xon": "18432"},
                              "pg_lossless_25000_40m_profile": {"size": "41984", "xon": "18432"},
                              "pg_lossless_40000_40m_profile": {"size": "45056", "xon": "18432"},
                              "pg_lossless_50000_40m_profile": {"size": "47104", "xon": "18432"},
                              "pg_lossless_100000_40m_profile": {"size": "59392", "xon": "18432"},
                              "pg_lossless_200000_40m_profile": {"size": "81920", "xon": "18432"},
                              "pg_lossless_1000_300m_profile": {"size": "37888", "xon": "18432"},
                              "pg_lossless_10000_300m_profile": {"size": "53248", "xon": "18432"},
                              "pg_lossless_25000_300m_profile": {"size": "78848", "xon": "18432"},
                              "pg_lossless_40000_300m_profile": {"size": "104448", "xon": "18432"},
                              "pg_lossless_50000_300m_profile": {"size": "121856", "xon": "18432"},
                              "pg_lossless_100000_300m_profile": {"size": "206848", "xon": "18432"},
                              "pg_lossless_200000_300m_profile": {"size": "376832", "xon": "18432"}},
            "spc2_3800_headroom": {"pg_lossless_1000_5m_profile": {"size": "32768", "xon": "18432"},
                                   "pg_lossless_10000_5m_profile": {"size": "34816", "xon": "18432"},
                                   "pg_lossless_25000_5m_profile": {"size": "38912", "xon": "18432"},
                                   "pg_lossless_40000_5m_profile": {"size": "41984", "xon": "18432"},
                                   "pg_lossless_50000_5m_profile": {"size": "44032", "xon": "18432"},
                                   "pg_lossless_100000_5m_profile": {"size": "55296", "xon": "18432"},
                                   "pg_lossless_200000_5m_profile": {"size": "77824", "xon": "18432"},
                                   "pg_lossless_1000_40m_profile": {"size": "33792", "xon": "18432"},
                                   "pg_lossless_10000_40m_profile": {"size": "36864", "xon": "18432"},
                                   "pg_lossless_25000_40m_profile": {"size": "43008", "xon": "18432"},
                                   "pg_lossless_40000_40m_profile": {"size": "49152", "xon": "18432"},
                                   "pg_lossless_50000_40m_profile": {"size": "53248", "xon": "18432"},
                                   "pg_lossless_100000_40m_profile": {"size": "72704", "xon": "18432"},
                                   "pg_lossless_200000_40m_profile": {"size": "112640", "xon": "18432"},
                                   "pg_lossless_1000_300m_profile": {"size": "34816", "xon": "18432"},
                                   "pg_lossless_10000_300m_profile": {"size": "50176", "xon": "18432"},
                                   "pg_lossless_25000_300m_profile": {"size": "75776", "xon": "18432"},
                                   "pg_lossless_40000_300m_profile": {"size": "101376", "xon": "18432"},
                                   "pg_lossless_50000_300m_profile": {"size": "117760", "xon": "18432"},
                                   "pg_lossless_100000_300m_profile": {"size": "202752", "xon": "18432"},
                                   "pg_lossless_200000_300m_profile": {"size": "373760", "xon": "18432"}},

            # Buffer profile info
            "buffer_profiles": {"ingress_lossless_profile": {"dynamic_th": "0", "pool": "[BUFFER_POOL|ingress_lossless_pool]", "size": "0"},
                                "ingress_lossy_profile": {"dynamic_th": "3", "pool": "[BUFFER_POOL|ingress_lossy_pool]", "size": "0"},
                                "egress_lossless_profile": {"dynamic_th": "7", "pool": "[BUFFER_POOL|egress_lossless_pool]", "size": "0"},
                                "egress_lossy_profile": {"dynamic_th": "3", "pool": "[BUFFER_POOL|egress_lossy_pool]", "size": "4096"},
                                "q_lossy_profile": {"dynamic_th": "3", "pool": "[BUFFER_POOL|egress_lossy_pool]", "size": "0"}}
        },
        "version_1_0_4": {
            # version 1.0.4 is introduced for updating the buffer settings
            "pool_configuration_list": ["spc1_t0_pool", "spc1_t1_pool", "spc2_t0_pool", "spc2_t1_pool", "spc2_3800_t0_pool", "spc2_3800_t1_pool"],

            # Buffer pool info for normal mode
            "buffer_pool_list" : ['ingress_lossless_pool', 'ingress_lossy_pool', 'egress_lossless_pool', 'egress_lossy_pool'],
            "spc1_t0_pool": {"ingress_lossless_pool": { "size": "4580864", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "4580864", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "13945824", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "4580864", "type": "egress", "mode": "dynamic" } },
            "spc1_t1_pool": {"ingress_lossless_pool": { "size": "3302912", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "3302912", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "13945824", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "3302912", "type": "egress", "mode": "dynamic" } },

            "spc2_t0_pool": {"ingress_lossless_pool": { "size": "14542848", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "14542848", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "34287552", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "14542848", "type": "egress", "mode": "dynamic" } },
            "spc2_t1_pool": {"ingress_lossless_pool": { "size": "11622400", "type": "ingress", "mode": "dynamic" },
                             "ingress_lossy_pool": { "size": "11622400", "type": "ingress", "mode": "dynamic" },
                             "egress_lossless_pool": { "size": "34287552", "type": "egress", "mode": "dynamic" },
                             "egress_lossy_pool": {"size": "11622400", "type": "egress", "mode": "dynamic" } },

            "spc2_3800_t0_pool": {"ingress_lossless_pool": { "size": "13924352", "type": "ingress", "mode": "dynamic" },
                                  "ingress_lossy_pool": { "size": "13924352", "type": "ingress", "mode": "dynamic" },
                                  "egress_lossless_pool": { "size": "34287552", "type": "egress", "mode": "dynamic" },
                                  "egress_lossy_pool": {"size": "13924352", "type": "egress", "mode": "dynamic" } },
            "spc2_3800_t1_pool": {"ingress_lossless_pool": { "size": "12457984", "type": "ingress", "mode": "dynamic" },
                                  "ingress_lossy_pool": { "size": "12457984", "type": "ingress", "mode": "dynamic" },
                                  "egress_lossless_pool": { "size": "34287552", "type": "egress", "mode": "dynamic" },
                                  "egress_lossy_pool": {"size": "12457984", "type": "egress", "mode": "dynamic" } },

            # Lossless headroom info
            "spc1_headroom": {"pg_lossless_10000_5m_profile": {"size": "49152", "xon":"19456"},
                              "pg_lossless_25000_5m_profile": {"size": "49152", "xon":"19456"},
                              "pg_lossless_40000_5m_profile": {"size": "49152", "xon":"19456"},
                              "pg_lossless_50000_5m_profile": {"size": "49152", "xon":"19456"},
                              "pg_lossless_100000_5m_profile": {"size": "50176", "xon":"19456"},
                              "pg_lossless_10000_40m_profile": {"size": "49152", "xon":"19456"},
                              "pg_lossless_25000_40m_profile": {"size": "51200", "xon":"19456"},
                              "pg_lossless_40000_40m_profile": {"size": "52224", "xon":"19456"},
                              "pg_lossless_50000_40m_profile": {"size": "53248", "xon":"19456"},
                              "pg_lossless_100000_40m_profile": {"size": "58368", "xon":"19456"},
                              "pg_lossless_10000_300m_profile": {"size": "56320", "xon":"19456"},
                              "pg_lossless_25000_300m_profile": {"size": "67584", "xon":"19456"},
                              "pg_lossless_40000_300m_profile": {"size": "78848", "xon":"19456"},
                              "pg_lossless_50000_300m_profile": {"size": "86016", "xon":"19456"},
                              "pg_lossless_100000_300m_profile": {"size": "123904", "xon":"19456"}},
            "spc2_headroom": {"pg_lossless_10000_5m_profile": {"size": "52224", "xon":"19456"},
                              "pg_lossless_25000_5m_profile": {"size": "52224", "xon":"19456"},
                              "pg_lossless_40000_5m_profile": {"size": "53248", "xon":"19456"},
                              "pg_lossless_50000_5m_profile": {"size": "53248", "xon":"19456"},
                              "pg_lossless_100000_5m_profile": {"size": "53248", "xon":"19456"},
                              "pg_lossless_200000_5m_profile": {"size": "55296", "xon":"19456"},
                              "pg_lossless_10000_40m_profile": {"size": "53248", "xon":"19456"},
                              "pg_lossless_25000_40m_profile": {"size": "55296", "xon":"19456"},
                              "pg_lossless_40000_40m_profile": {"size": "57344", "xon":"19456"},
                              "pg_lossless_50000_40m_profile": {"size": "58368", "xon":"19456"},
                              "pg_lossless_100000_40m_profile": {"size": "63488", "xon":"19456"},
                              "pg_lossless_200000_40m_profile": {"size": "74752", "xon":"19456"},
                              "pg_lossless_10000_300m_profile": {"size": "60416", "xon":"19456"},
                              "pg_lossless_25000_300m_profile": {"size": "73728", "xon":"19456"},
                              "pg_lossless_40000_300m_profile": {"size": "86016", "xon":"19456"},
                              "pg_lossless_50000_300m_profile": {"size": "95232", "xon":"19456"},
                              "pg_lossless_100000_300m_profile": {"size": "137216", "xon":"19456"},
                              "pg_lossless_200000_300m_profile": {"size": "223232", "xon":"19456"}},
            "spc2_3800_headroom": {"pg_lossless_10000_5m_profile": {"size": "54272", "xon":"19456"},
                                   "pg_lossless_25000_5m_profile": {"size": "58368", "xon":"19456"},
                                   "pg_lossless_40000_5m_profile": {"size": "61440", "xon":"19456"},
                                   "pg_lossless_50000_5m_profile": {"size": "64512", "xon":"19456"},
                                   "pg_lossless_100000_5m_profile": {"size": "75776", "xon":"19456"},
                                   "pg_lossless_10000_40m_profile": {"size": "55296", "xon":"19456"},
                                   "pg_lossless_25000_40m_profile": {"size": "60416", "xon":"19456"},
                                   "pg_lossless_40000_40m_profile": {"size": "65536", "xon":"19456"},
                                   "pg_lossless_50000_40m_profile": {"size": "69632", "xon":"19456"},
                                   "pg_lossless_100000_40m_profile": {"size": "86016", "xon":"19456"},
                                   "pg_lossless_10000_300m_profile": {"size": "63488", "xon":"19456"},
                                   "pg_lossless_25000_300m_profile": {"size": "78848", "xon":"19456"},
                                   "pg_lossless_40000_300m_profile": {"size": "95232", "xon":"19456"},
                                   "pg_lossless_50000_300m_profile": {"size": "106496", "xon":"19456"},
                                   "pg_lossless_100000_300m_profile": {"size": "159744", "xon":"19456"}},

            # Buffer profile info
            "buffer_profiles": {"ingress_lossless_profile": {"dynamic_th": "7", "pool": "[BUFFER_POOL|ingress_lossless_pool]", "size": "0"},
                                "ingress_lossy_profile": {"dynamic_th": "3", "pool": "[BUFFER_POOL|ingress_lossy_pool]", "size": "0"},
                                "egress_lossless_profile": {"dynamic_th": "7", "pool": "[BUFFER_POOL|egress_lossless_pool]", "size": "0"},
                                "egress_lossy_profile": {"dynamic_th": "7", "pool": "[BUFFER_POOL|egress_lossy_pool]", "size": "9216"},
                                "q_lossy_profile": {"dynamic_th": "3", "pool": "[BUFFER_POOL|egress_lossy_pool]", "size": "0"}}
        }
    }

    def mlnx_default_buffer_parameters(self, db_version, table):
        """
        We extract buffer configurations to a common function
        so that it can be reused among different migration
        The logic of buffer parameters migrating:
        1. Compare the current buffer configuration with the default settings
        2. If there is a match, migrate the old value to the new one
        3. Insert the new setting into database
        Each settings defined below (except that for version_1_0_2) will be used twice:
        1. It is referenced as new setting when database is migrated to that version
        2. It is referenced as old setting when database is migrated from that version
        """

        return self.mellanox_default_parameter[db_version].get(table)

    def mlnx_migrate_buffer_pool_size(self, old_version, new_version):
        """
        To migrate buffer pool configuration
        """
        # Buffer pools defined in old version
        old_default_buffer_pools = self.mlnx_default_buffer_parameters(old_version, "buffer_pool_list")

        # Try to get related info from DB
        buffer_pool_conf_in_db = self.configDB.get_table('BUFFER_POOL')

        # Get current buffer pool configuration, only migrate configuration which
        # with default values, if it's not default, leave it as is.
        name_list_of_pools_in_db = buffer_pool_conf_in_db.keys()

        # Buffer pool numbers is different with default, don't need migrate
        if len(name_list_of_pools_in_db) != len(old_default_buffer_pools):
            log.log_notice("Pools in CONFIG_DB ({}) don't match default ({}), skip buffer pool migration".format(name_list_of_pools_in_db, old_default_buffer_pools))
            return True

        # If some buffer pool is not default ones, don't need migrate
        for buffer_pool in old_default_buffer_pools:
            if buffer_pool not in name_list_of_pools_in_db:
                log.log_notice("Default pool {} isn't in CONFIG_DB, skip buffer pool migration".format(buffer_pool))
                return True

        old_pool_configuration_list = self.mlnx_default_buffer_parameters(old_version, "pool_configuration_list")
        if not old_pool_configuration_list:
            log.log_error("Trying to get pool configuration list or migration control failed, skip migration")
            return False

        new_config_name = None
        for old_config_name in old_pool_configuration_list:
            old_config = self.mlnx_default_buffer_parameters(old_version, old_config_name)
            log.log_info("Checking old pool configuration {}".format(old_config_name))
            if buffer_pool_conf_in_db == old_config:
                new_config_name = old_config_name
                log.log_info("Old buffer pool configuration {} will be migrate to new one".format(old_config_name))
                break

        if not new_config_name:
            log.log_notice("The configuration doesn't match any default configuration, migration for pool isn't required")
            return True

        new_buffer_pool_conf = self.mlnx_default_buffer_parameters(new_version, new_config_name)
        if not new_buffer_pool_conf:
            log.log_error("Can't find the buffer pool configuration for {} in {}".format(new_config_name, new_version))
            return False

        # Migrate old buffer conf to latest.
        for pool in old_default_buffer_pools:
            self.configDB.set_entry('BUFFER_POOL', pool, new_buffer_pool_conf.get(pool))

            log.log_info("Successfully migrate mlnx buffer pool {} size to the latest.".format(pool))

        return True

    def mlnx_migrate_buffer_profile(self, old_version, new_version):
        """
        This is to migrate BUFFER_PROFILE configuration
        """
        device_data = self.configDB.get_table('DEVICE_METADATA')
        if 'localhost' in device_data.keys():
            platform = device_data['localhost']['platform']
        else:
            log.log_error("Trying to get DEVICE_METADATA from DB but doesn't exist, skip migration")
            return False

        spc1_platforms = ["x86_64-mlnx_msn2010-r0", "x86_64-mlnx_msn2100-r0", "x86_64-mlnx_msn2410-r0", "x86_64-mlnx_msn2700-r0", "x86_64-mlnx_msn2740-r0"]
        spc2_platforms = ["x86_64-mlnx_msn3700-r0", "x86_64-mlnx_msn3700c-r0"]

        # get profile
        buffer_profile_old_configure = self.mlnx_default_buffer_parameters(old_version, "buffer_profiles")
        buffer_profile_new_configure = self.mlnx_default_buffer_parameters(new_version, "buffer_profiles")

        buffer_profile_conf = self.configDB.get_table('BUFFER_PROFILE')

        # we need to transform lossless pg profiles to new settings
        # to achieve that, we just need to remove this kind of profiles, buffermgrd will generate them automatically
        default_lossless_profiles = None
        if platform == 'x86_64-mlnx_msn3800-r0':
            default_lossless_profiles = self.mlnx_default_buffer_parameters(old_version, "spc2_3800_headroom")
            new_lossless_profiles = self.mlnx_default_buffer_parameters(new_version, "spc2_3800_headroom")
        elif platform in spc2_platforms:
            default_lossless_profiles = self.mlnx_default_buffer_parameters(old_version, "spc2_headroom")
            new_lossless_profiles = self.mlnx_default_buffer_parameters(new_version, "spc2_headroom")
        elif platform in spc1_platforms:
            default_lossless_profiles = self.mlnx_default_buffer_parameters(old_version, "spc1_headroom")
            new_lossless_profiles = self.mlnx_default_buffer_parameters(new_version, "spc1_headroom")

        if default_lossless_profiles and new_lossless_profiles:
            for name, profile in buffer_profile_conf.iteritems():
                if name in default_lossless_profiles.keys():
                    default_profile = default_lossless_profiles.get(name)
                    new_profile = new_lossless_profiles.get(name)
                    if not default_profile or not new_profile:
                        continue
                    default_profile['dynamic_th'] = '0'
                    default_profile['xoff'] = str(int(default_profile['size']) - int(default_profile['xon']))
                    default_profile['pool'] = '[BUFFER_POOL|ingress_lossless_pool]'
                    if profile == default_profile:
                        default_profile['size'] = new_profile['size']
                        default_profile['xon'] = new_profile['xon']
                        default_profile['xoff'] = str(int(default_profile['size']) - int(default_profile['xon']))
                        self.configDB.set_entry('BUFFER_PROFILE', name, default_profile)

        if not buffer_profile_new_configure:
            # Not providing new profile configure in new version means they do need to be changed
            log.log_notice("No buffer profile in {}, don't need to migrate non-lossless profiles".format(new_version))
            return True

        for name, profile in buffer_profile_old_configure.iteritems():
            if name in buffer_profile_conf.keys() and profile == buffer_profile_old_configure[name]:
                continue
            # return if any default profile isn't in cofiguration
            log.log_notice("Default profile {} isn't in database or doesn't match default value".format(name))
            return True

        for name, profile in buffer_profile_new_configure.iteritems():
            log.log_info("Successfully migrate profile {}".format(name))
            self.configDB.set_entry('BUFFER_PROFILE', name, profile)
