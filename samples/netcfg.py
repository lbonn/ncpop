#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Little wifi selector for Archlinux (netcfg)
'''

import os
import os.path
import subprocess
import sys

import ncpop

app_title = "ncf : select a wifi network"
term_name = "/usr/bin/urxvt -geometry 30x20 -title ncfg -name ncfg"
netcfg_path = "/usr/bin/netcfg"
network_d_path = "/etc/network.d"

def conf_handler(cfg):
    return subprocess.call([netcfg_path, cfg])

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-spawn':
        return ncpop.exec_in_term(__file__, term_name)

    confs = [c for c in os.listdir(network_d_path)
            if os.path.isfile(network_d_path + "/" + c)]
    confs = sorted(confs, key=str.lower)

    ncpop.popup(sys.argv, app_title, confs, conf_handler)


if __name__ == "__main__":
    sys.exit(main())
