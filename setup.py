import glob
import sys
from setuptools import setup
import unittest

# For python3 wheel, we currently don't need test
# TODO: build python3 wheel of all the dependencies, and remove conditional test
def get_test_suite():
    if sys.version_info >= (3, 0):
        return unittest.TestSuite()
    else:
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('sonic-utilities-tests', pattern='*.py')
        return test_suite

setup(
    name='sonic-utilities',
    version='1.1',
    description='Command-line utilities for SONiC',
    license='Apache 2.0',
    author='SONiC Team',
    author_email='linuxnetdev@microsoft.com',
    url='https://github.com/Azure/sonic-utilities',
    maintainer='Joe LeVeque',
    maintainer_email='jolevequ@microsoft.com',
    packages=[
        'acl_loader',
        'clear',
        'config',
        'debug',
        'pfcwd',
        'sfputil',
        'psuutil',
        'show',
        'sonic_eeprom',
        'sonic_installer',
        'sonic_psu',
        'sonic_sfp',
        'sonic-utilities-tests',
        'undebug',
    ],
    package_data={
        'show': ['aliases.ini']
    },
    scripts=[
        'scripts/aclshow',
        'scripts/boot_part',
        'scripts/coredump-compress',
        'scripts/decode-syseeprom',
        'scripts/dropcheck',
        'scripts/ecnconfig',
        'scripts/fast-reboot',
        'scripts/fast-reboot-dump.py',
        'scripts/fdbshow',
        'scripts/generate_dump',
        'scripts/intfutil',
        'scripts/lldpshow',
        'scripts/port2alias',
        'scripts/portstat',
        'scripts/teamshow',
        'scripts/config-hwsku.sh',
    ],
    data_files=[
        ('/etc/bash_completion.d', glob.glob('data/etc/bash_completion.d/*')),
    ],
    entry_points={
        'console_scripts': [
            'acl-loader = acl_loader.main:cli',
            'config = config.main:cli',
            'debug = debug.main:cli',
            'pfcwd = pfcwd.main:cli',
            'sfputil = sfputil.main:cli',
            'psuutil = psuutil.main:cli',
            'show = show.main:cli',
            'sonic-clear = clear.main:cli',
            'sonic_installer = sonic_installer.main:cli',
            'undebug = undebug.main:cli',
        ]
    },
    install_requires=[
        'click-default-group',
        'click',
        'natsort',
        'tabulate'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords='sonic SONiC utilities command line cli CLI',
    test_suite='setup.get_test_suite'
)
