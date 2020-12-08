import socket
import traceback
import requests

# socket de UDP
udp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# socket RAW de citire a răspunsurilor ICMP
icmp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
# setam timout in cazul in care socketul ICMP la apelul recvfrom nu primeste nimic in buffer
icmp_recv_socket.settimeout(3)


def traceroute(TTL, ip, port):

    # setam TTL in headerul de IP pentru socketul de UDP
    udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

    # trimite un mesaj UDP catre un tuplu (IP, port)
    udp_send_sock.sendto(b'salut', (ip, port))

    addr = 'done!'
    try:
        data, (addr, port)  = icmp_recv_socket.recvfrom(63535)
    except Exception as e:
        print("Socket timeout ", str(e))
        print(traceback.format_exc())

    return addr


def get_location_info(ip_address):
    "Obține informații despre localizarea unei adrese IP"

    fields = [
        'status',
        'country',
        'regionName',
        'city',
    ]
    params = {
        'fields': ','.join(fields)
    }
    response = requests.get(f'http://ip-api.com/json/{ip_address}', params=params)

    data = response.json()

    if data['status'] == 'success':
        return f"{data['country']}, {data['regionName']}, {data['city']}"

    return "UNKNOWN"

def main():

    TTL = 1
    dest_ip = '172.217.17.132'
    my_ip =  ''
    port = 80
    ip_addresses = []
    # inseamna ca nu e o adresa pe care o putem folosi
    while my_ip != dest_ip:
        my_ip = traceroute(TTL, dest_ip, port)
        if my_ip != 'done!':
            print(my_ip)
            ip_addresses.append(my_ip)
        TTL += 1


    for ip_addr in ip_addresses:
        print(ip_addr, '-', get_location_info(ip_addr))

if __name__ == '__main__':
    main()
