from collections import OrderedDict


def validate(s: str):
    chsms = OrderedDict()
    i = iter(s)
    lchunk = ''
    while True:
        chunk = ''
        cntr = 4
        while len(chunk) < cntr:
            chunk += next(i)

        if chunk == 'X@y$':
            continue

        if chunk == 'A#<B':
            break

        #if chunk not in chsms:
        if lchunk != chunk:
            chsms[chunk] = 0

        lchunk = chunk
        cntr = int(next(i) + next(i))
        chunk = ''
        while len(chunk) < cntr:
            chunk += next(i)

        c = 0xFFFF
        for char in chunk:
            c ^= ord(char)
            for _ in range(8):
                if c & 0x0001:
                    c >>= 1
                    c ^= 0xA001
                else:
                    c >>= 1
        chsms[lchunk] += c

    chunk = ''.join(map(str, chsms.values()))
    c = 0xFFFF
    for char in chunk:
        c ^= ord(char)
        for _ in range(8):
            if c & 0x0001:
                c >>= 1
                c ^= 0xA001
            else:
                c >>= 1
    calc = c
    f = ''.join([next(i) for _ in range(5)])

    return str(f) == str(calc) or str(f[:4]) == str(calc)


def main():
    # s = 'dQEu06KFs1nRX@y$WjjR10Bk6bzHFlBCX@y$WjjR099RrVhBgNUX@y$15Hs02THX@y$15Hs01XX@y$15Hs03BjrX@y$WjjR05Hq1xwX@y$9eeI06VOSD5xX@y$A#<B-6576894852221858211'
    #s = 'WVAF06hv8C5XX@y$fUH702suX@y$fUH704jR7tX@y$zg7u055oT9pX@y$zg7u06QNOBS6X@y$zg7u08DfnjgSvUX@y$fUH702kmX@y$zOjI05g9CejX@y$A#<B34749'
    s = 'PCtq02qnX@y$QLKD04jo5AX@y$QLKD03ahvX@y$bBGP06PzWh0VX@y$bBGP05CHYCfX@y$bBGP05s5rkSX@y$QLKD065Z2gFCX@y$A#<B26622'
    if validate(s):
        print(':)')
    else:
        print(':(')


if __name__ == '__main__':
    main()
