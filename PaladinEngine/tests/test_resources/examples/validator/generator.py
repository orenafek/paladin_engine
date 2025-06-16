import hashlib
import random
import string

SEP = 'X@y$'
FINAL = 'A#<B'
N = 15
I = 0


def gen_str(length: int):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


magic_options = [gen_str(4) for _ in range(int(N))]
magic_seq = [1, 2, 3, 'X', 1, 1, 'Y', 2, 1, 1, 3]
magic_seq2 = [2, 1, 1, 3, 1, 1, 2, 1, 2, 3]
magics = []


def populate_magics(seq):
    global magics
    for i, c in enumerate(seq):
        if c == 'X':
            c = 1
            i = 1
        if c == 'Y':
            c = 1
            i = 2

        magics.extend([magic_options[i] for _ in range(c)])

    return magics


def generate_msg():
    return str(msg(magic := gen_magic(), l := gen_len(), (cntnt := gen_str(int(l))), SEP)), magic, cntnt


def crc16(data):
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char)
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class msg(object):
    def __init__(self, magic, l, content, sep):
        self.magic: str = magic
        self.len: str = l
        self.content: str = content
        self.sep: str = sep

    def __repr__(self):
        return f'{self.magic}{self.len}{self.content}{self.sep}'


def gen_magic():
    global I
    m = magics[I]
    I += 1
    return m


def gen_len():
    n = random.randint(1, 10)
    return str(n) if n >= 10 else f'0{n}'


def gen_input():
    s = ''
    cntnts = {}
    for _ in range(N):
        msg, magic, content = generate_msg()
        s += msg
        if magic not in cntnts:
            cntnts[magic] = 0
        cntnts[magic] += (c := crc16(content))
        print(f'{magic}: {c}')

    print(''.join(map(str, cntnts.values())))
    checksum = hashlib.md5(''.join(map(str, cntnts.values())).encode()).hexdigest()
    print(len(str(checksum)))
    return f'{s}{FINAL}{checksum}'


def main():
    populate_magics(magic_seq)
    print(gen_input())
    populate_magics(magic_seq2)
    print(gen_input())

if __name__ == '__main__':
    main()
