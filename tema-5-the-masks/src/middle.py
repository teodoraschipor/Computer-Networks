import socket
import logging
import time
from scapy.all import *


def function(pkt):
    pkt[IP].src = '198.7.0.1' # sursa va fi router-ul
    pkt[IP].dst = '198.7.0.2' # trimite server-ului
    sendp(pkt)

pkts = sniff(iface='eth0', filter="tcp and host 198.7.0.1", prn=function) # primeste pachetele de tip tcp de la router; function -- le modifica si le trimite catre server ca si cum ar fi clientul


