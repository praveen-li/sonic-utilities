#!/usr/bin/python

""""
Description: dump_nat_entries.py -- dump conntrack nat entries from kernel into a file
             so as to restore them during warm reboot
"""

import sys
import subprocess

def main():
    ctdumpcmd = 'conntrack -L -j > /host/warmboot/nat/nat_entries.dump'
    p = subprocess.Popen(ctdumpcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, err) = p.communicate()
    rc = p.wait()
    
    if rc != 0:
        print("Dumping conntrack entries failed")
    return

if __name__ == '__main__':
    main()
