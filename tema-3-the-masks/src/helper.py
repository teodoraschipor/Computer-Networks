import struct
import socket
import logging

MAX_UINT32 = 0xFFFFFFFF
MAX_BITI_CHECKSUM = 16
MAX_SEGMENT = 1400

def compara_endianness(numar):
    '''
    https://en.m.wikipedia.org/wiki/Endianness#Etymology
        numarul 16 se scrie in binar 10000 (2^4)
        pe 8 biti, adaugam 0 pe pozitiile mai mari: 00010000
        pe 16 biti, mai adauga un octet de 0 pe pozitiile mai mari: 00000000 00010000
        daca numaratoarea incepe de la dreapta la stanga:
            reprezentarea Big Endian (Network Order) este: 00000000 00010000
                - cel mai semnificativ bit are adresa cea mai mica
            reprezentarea Little Endian este: 00010000 00000000
                - cel mai semnificativ bit are adresa cea mai mare
    '''
    print ("Numarul: ", numar)
    print ("Network Order (Big Endian): ", [bin(byte) for byte in struct.pack('!H', numar)])
    print ("Little Endian: ", [bin(byte) for byte in struct.pack('<H', numar)])


def create_header_emitator(seq_nr, checksum, flags='S'):

    var = 0

    if flags == 'S':
        var = var | 0b100
    elif flags == 'F':
        var = var | 0b001
    elif flags == 'P':
        var = var | 0b010
    octeti = struct.pack('!LHH', seq_nr, checksum, var)
    return octeti


def parse_header_emitator(octeti):

    seq_nr, checksum, spf = struct.unpack('!LHH', octeti)
    flags = ''
    if spf & 0b100:
        # inseamna ca am primit S
        flags = 'S'
    elif spf & 0b001:
        # inseamna ca am primit F
        flags = 'F'
    elif spf & 0b010:
        # inseamna ca am primit P
        flags = 'P'
    return (seq_nr, checksum, flags)


def create_header_receptor(ack_nr, checksum, window):

    octeti = struct.pack('!LHH', ack_nr, checksum, window)
    return octeti


def parse_header_receptor(octeti):

    ack_nr, checksum, window = struct.unpack('!LHH', octeti)
    return (ack_nr, checksum, window)


def citeste_segment(file_descriptor):
    '''
        generator, returneaza cate un segment de 1400 de octeti dintr-un fisier
    '''
    yield file_descriptor.read(MAX_SEGMENT)


def exemplu_citire(cale_catre_fisier):
    with open(cale_catre_fisier, 'rb') as file_in:
        for segment in citeste_segment(file_in):
            print(segment)


def calculeaza_checksum(octeti):

    checksum = 0
    # daca lungimea len(octeti) este impară, se mai adaugă un octet de 0 la sfârșit
    if len(octeti) % 2 == 1:
        octeti.ljust(len(octeti) + 8, '0')

    max_biti = 16
    max_nr = (1 << max_biti) - 1
    n = len(octeti)
    numbers = []
    # 1. convertim sirul octeti in numere pe 16 biti:
    for i in range(0, n, 2):
        number = int(struct.unpack('!H', octeti[i:i+2])[0]) # cate un numar de 16 biti
        numbers.append(number)
    #print(numbers)

    # 2. adunam numerele in complementul lui 1, ce depaseste 16 biti se aduna la coada:
    for i in range(len(numbers)):
        a = numbers[i]
        checksum = (checksum + a) % max_nr
        #print(bin(checksum))

    # 3. complementarea bitilor sumei
    checksum = ~(-checksum)
    #print(bin(checksum))

    return checksum


def verifica_checksum(octeti):
    if calculeaza_checksum(octeti):
        return True
    return False



if __name__ == '__main__':
    compara_endianness(16)
   # Verif. checksum:
   # z = struct.pack('!HH',65535, 2)
   # g = calculeaza_checksum(z)
   # print(g)
