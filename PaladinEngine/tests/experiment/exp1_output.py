from stubs.stubs import __AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__, __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__


"""
__     __        _  _      _         _
\\ \\   / /  __ _ | |(_)  __| |  __ _ | |_   ___   _ __
 \\ \\ / /  / _` || || | / _` | / _` || __| / _ \\ | '__|
  \\ V /  | (_| || || || (_| || (_| || |_ | (_) || |
   \\_/    \\__,_||_||_| \\__,_| \\__,_| \\__| \\___/ |_|

This program validates a string sequence generated by the generator program.
The string should consist of messages, each be in the following format:
Message: <Magic |4|><Length|2|><Content|Length|>
The generator program calculates a checksum on each message content.

The entire sequence is in the following format:
Sequence: <Message><Seperator><Message><Seperator>...<Message><Seperator><EndBarker><Entire Seq.Checksum>

The entire sequence checksum is calculated by running md5sum on the result of string-concatenating the sums of crc32
on the content of messages with the same magic.
"""
import binascii
import hashlib
from collections import OrderedDict

def crc(inp: str):
    __DEF__('crc', line_no=24, frame=__FRAME__())
    __ARG__('crc', __FRAME__(), 24, inp=inp)
    __UNDEF__('crc', __FRAME__(), 25)
    return __FC__("binascii.crc32(bytes(inp, 'utf-8'))", binascii.crc32, locals(), globals(), __FRAME__(), 25, bytes(inp, 'utf-8'))

def validate(s: str):
    __DEF__('validate', line_no=28, frame=__FRAME__())
    __ARG__('validate', __FRAME__(), 28, s=s)
    chsms = __FC__('OrderedDict()', OrderedDict, locals(), globals(), __FRAME__(), 29)
    __AS__('chsms = __FC__(@OrderedDict()@, OrderedDict, locals(), globals(), __FRAME__(), 29)', 'chsms', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=29)
    i = 0
    __AS__('i = 0', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=30)
    cursum = 0
    __AS__('cursum = 0', 'cursum', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=31)
    lchunk = ''
    __AS__('lchunk = @@', 'lchunk', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=32)
    __SOL__(__FRAME__(), 33)
    while True:
        __SOLI__(33, __FRAME__())
        cntr = 4
        __AS__('cntr = 4', 'cntr', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=34)
        chunk = s[i:i + cntr]
        __AS__('chunk = s[i:i + cntr]', 'chunk', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=35)
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__0__LINE_NO__36 = i + cntr
        i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__0__LINE_NO__36
        __AS__('i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__0__LINE_NO__36', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=36)
        if chunk == 'X@y$':
            __EOLI__(__FRAME__(), loop_start_line_no=33, loop_end_line_no=55)
            continue
        if lchunk and lchunk != chunk:
            chsms[lchunk] = cursum
            __AS__('chsms[lchunk] = cursum', 'chsms[lchunk]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=42)
            cursum = 0
            __AS__('cursum = 0', 'cursum', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=43)
        if chunk == 'A#<B':
            __EOLI__(__FRAME__(), loop_start_line_no=33, loop_end_line_no=55)
            __BREAK__(frame=__FRAME__(), line_no=46)
            break
        lchunk = chunk
        __AS__('lchunk = chunk', 'lchunk', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=48)
        cntr = __FC__('int(s[i] + s[i + 1])', int, locals(), globals(), __FRAME__(), 49, s[i] + s[i + 1])
        __AS__('cntr = __FC__(@int(s[i] + s[i + 1])@, int, locals(), globals(), __FRAME__(), 49, s[i] + s[i + 1])', 'cntr', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=49)
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__1__LINE_NO__36 = i + 2
        i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__1__LINE_NO__36
        __AS__('i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__1__LINE_NO__36', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=50)
        chunk = s[i:i + cntr]
        __AS__('chunk = s[i:i + cntr]', 'chunk', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=52)
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__2__LINE_NO__36 = i + cntr
        i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__2__LINE_NO__36
        __AS__('i = ____PALADIN_TEMP_AUG_ASSIGN_VAR__2__LINE_NO__36', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=53)
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__3__LINE_NO__36 = cursum + crc(chunk)
        cursum = ____PALADIN_TEMP_AUG_ASSIGN_VAR__3__LINE_NO__36
        __AS__('cursum = ____PALADIN_TEMP_AUG_ASSIGN_VAR__3__LINE_NO__36', 'cursum', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=55)
        __EOLI__(__FRAME__(), loop_start_line_no=33, loop_end_line_no=55)
    chunk = __FC__("''.join(map(str, __FC__('chsms.values()', chsms.values, locals(), globals(), __FRAME__(), 57)))", ''.join, locals(), globals(), __FRAME__(), 57, map(str, __FC__('chsms.values()', chsms.values, locals(), globals(), __FRAME__(), 57)))
    __AS__('chunk = __FC__(@@@.join(map(str, __FC__(@chsms.values()@, chsms.values, locals(), globals(), __FRAME__(), 57)))@, @@.join, locals(), globals(), __FRAME__(), 57, map(str, __FC__(@chsms.values()@, chsms.values, locals(), globals(), __FRAME__(), 57)))', 'chunk', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=57)
    calc = __FC__("__FC__('hashlib.md5(chunk.encode())', hashlib.md5, locals(), globals(), __FRAME__(), 58, chunk.encode()).hexdigest()", __FC__('hashlib.md5(chunk.encode())', hashlib.md5, locals(), globals(), __FRAME__(), 58, chunk.encode()).hexdigest, locals(), globals(), __FRAME__(), 58)
    __AS__('calc = __FC__(@__FC__(@hashlib.md5(chunk.encode())@, hashlib.md5, locals(), globals(), __FRAME__(), 58, chunk.encode()).hexdigest()@, __FC__(@hashlib.md5(chunk.encode())@, hashlib.md5, locals(), globals(), __FRAME__(), 58, chunk.encode()).hexdigest, locals(), globals(), __FRAME__(), 58)', 'calc', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=58)
    f = __FC__("''.join([s[i + _] for _ in __FC__('range(32)', range, locals(), globals(), __FRAME__(), 59, 32)])", ''.join, locals(), globals(), __FRAME__(), 59, [s[i + _] for _ in __FC__('range(32)', range, locals(), globals(), __FRAME__(), 59, 32)])
    __AS__('f = __FC__(@@@.join([s[i + _] for _ in __FC__(@range(32)@, range, locals(), globals(), __FRAME__(), 59, 32)])@, @@.join, locals(), globals(), __FRAME__(), 59, [s[i + _] for _ in __FC__(@range(32)@, range, locals(), globals(), __FRAME__(), 59, 32)])', 'f', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=59)
    __UNDEF__('validate', __FRAME__(), 61)
    return __FC__('str(f)', str, locals(), globals(), __FRAME__(), 61, f) == __FC__('str(calc)', str, locals(), globals(), __FRAME__(), 61, calc)

def validate_input(s: str):
    __DEF__('validate_input', line_no=64, frame=__FRAME__())
    __ARG__('validate_input', __FRAME__(), 64, s=s)
    if __FC__('validate(s)', validate, locals(), globals(), __FRAME__(), 65, s):
        __PRINT__(66, __FRAME__(), ':)')
    else:
        __PRINT__(68, __FRAME__(), ':(')
    __UNDEF__('validate_input', __FRAME__(), 68)
    return None

def main():
    __DEF__('main', line_no=71, frame=__FRAME__())
    __ARG__('main', __FRAME__(), 71)
    s1 = 'u4kE08wNrEvl1IX@y$g1p204J0wYX@y$g1p206nJhkDzX@y$vyvo05UuFEdX@y$9JpA01fX@y$9JpA012X@y$tSvh06EL5k2DX@y$ZUKq03D45X@y$b7FN03beoX@y$b7FN04xRSgX@y$b7FN08UTwWczOEX@y$JqU0052GmxzX@y$GAKn01oX@y$lxU803b5ZX@y$lxU8045diaX@y$KeeD09RTwsyZ2aoX@y$grh110EEW6uj2slzX@y$grh103TvtX@y$OLt101RX@y$OLt1081mxzj7dsX@y$OLt104T3TOX@y$ahTW10Q0DE6b17zTX@y$ahTW07ducYmnvX@y$xF4j09vzSlMjepxX@y$DUUl05oCjgEX@y$DUUl02DvX@y$DUUl05lqhCiX@y$V9Ma06xIQVJUX@y$V9Ma086nKV82MrX@y$V9Ma03bTEX@y$A#<B7f14990ec00a36145fa897b6744acb8f'
    __AS__('s1 = @u4kE08wNrEvl1IX@y$g1p204J0wYX@y$g1p206nJhkDzX@y$vyvo05UuFEdX@y$9JpA01fX@y$9JpA012X@y$tSvh06EL5k2DX@y$ZUKq03D45X@y$b7FN03beoX@y$b7FN04xRSgX@y$b7FN08UTwWczOEX@y$JqU0052GmxzX@y$GAKn01oX@y$lxU803b5ZX@y$lxU8045diaX@y$KeeD09RTwsyZ2aoX@y$grh110EEW6uj2slzX@y$grh103TvtX@y$OLt101RX@y$OLt1081mxzj7dsX@y$OLt104T3TOX@y$ahTW10Q0DE6b17zTX@y$ahTW07ducYmnvX@y$xF4j09vzSlMjepxX@y$DUUl05oCjgEX@y$DUUl02DvX@y$DUUl05lqhCiX@y$V9Ma06xIQVJUX@y$V9Ma086nKV82MrX@y$V9Ma03bTEX@y$A#<B7f14990ec00a36145fa897b6744acb8f@', 's1', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=72)
    __FC__('validate_input(s1)', validate_input, locals(), globals(), __FRAME__(), 73, s1)
    s2 = 'V9Ma01EX@y$Rttb05cFeEoX@y$Rttb03rNCX@y$Trkg09AFdU0FxoEX@y$oX3A082AIBHJ48X@y$u4kE06MB1NO4X@y$g1p206DtiFSrX@y$g1p210wj91OXa1QRX@y$vyvo08rSsE3pJRX@y$vyvo03rtmX@y$9JpA07A2YjMFAX@y$tSvh018X@y$tSvh08hv7yaRgqX@y$tSvh01XX@y$g1p207o5dDENwX@y$b7FN08THvPpRTPX@y$JqU0017X@y$vyvo03tpjX@y$lxU809NKBiB6lPsX@y$lxU804aYTaX@y$KeeD09Ev136BTisX@y$grh107rkMbfMpX@y$OLt108FvqPZcauX@y$OLt102ufX@y$OLt101KX@y$ahTW09F6RXcF5TSX@y$ahTW02T5X@y$xF4j02TSX@y$DUUl041wZzX@y$V9Ma05HO6tvX@y$A#<B635f36a2d8a4c09efbfc396c3cf7df77'
    __AS__('s2 = @V9Ma01EX@y$Rttb05cFeEoX@y$Rttb03rNCX@y$Trkg09AFdU0FxoEX@y$oX3A082AIBHJ48X@y$u4kE06MB1NO4X@y$g1p206DtiFSrX@y$g1p210wj91OXa1QRX@y$vyvo08rSsE3pJRX@y$vyvo03rtmX@y$9JpA07A2YjMFAX@y$tSvh018X@y$tSvh08hv7yaRgqX@y$tSvh01XX@y$g1p207o5dDENwX@y$b7FN08THvPpRTPX@y$JqU0017X@y$vyvo03tpjX@y$lxU809NKBiB6lPsX@y$lxU804aYTaX@y$KeeD09Ev136BTisX@y$grh107rkMbfMpX@y$OLt108FvqPZcauX@y$OLt102ufX@y$OLt101KX@y$ahTW09F6RXcF5TSX@y$ahTW02T5X@y$xF4j02TSX@y$DUUl041wZzX@y$V9Ma05HO6tvX@y$A#<B635f36a2d8a4c09efbfc396c3cf7df77@', 's2', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=74)
    __FC__('validate_input(s2)', validate_input, locals(), globals(), __FRAME__(), 75, s2)
    __UNDEF__('main', __FRAME__(), 75)
    return None
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__(), 79)