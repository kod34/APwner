#!/usr/bin/env python3

from os import geteuid
from mods.functions import *
from mods.args import *
import threading
import sys

if geteuid() != 0:
    sys.exit(color.YELLOW+"Run as root!"+color.END)
if args.Handshake:
    print(banner)
    get_interface()


    change_mac()
    check_kill()
    airodump()
    read_dump()
    airmon()
    read_dump_s()
    t1 = threading.Thread(target=ddos)
    t2 = threading.Thread(target=handshake)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


elif args.Dos:
    print(banner)
    get_interface()


    change_mac()
    check_kill()
    airodump()
    read_dump()
    airmon()
    read_dump_s()
    ddos()

else:
    parser.error("Select a mode")
