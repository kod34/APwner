#!/bin/bash
sudo apt install aircrack-ng macchanger xterm python3-pip -y
sudo pip3 install psutil prettytable
sudo ln -s $(readlink -f codice.py) ${PATH%%:*}/codice
