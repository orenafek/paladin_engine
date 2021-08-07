from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__, __IF__


if __IF__(1 > 0, '1 > 0', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10):
    __FC__("print('1 > 0')", print, locals(), globals(), __FRAME__, 2, '1 > 0')
if __IF__(0 == 0 or 9 == 9, "'0 == 0'", "'9 == 9'", 'or', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10):
    __FC__("print('0 == 0 or 9 == 9')", print, locals(), globals(), __FRAME__, 2, '0 == 0 or 9 == 9')
if __IF__(1 < 2 or 3 > 5, "'1 < 2'", "'3 > 5'", 'or', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10):
    __FC__("print('1 < 2 or (3 > 5)')", print, locals(), globals(), __FRAME__, 2, '1 < 2 or (3 > 5)')
square = lambda x: x * x
__AS__('square = lambda x: x * x', 'square', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10)
if __IF__(__FC__('square(3)', square, locals(), globals(), __FRAME__, 1, 3) == 9, 'square(3) == 9', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10):
    __FC__("print('square(3) == 9')", print, locals(), globals(), __FRAME__, 2, 'square(3) == 9')