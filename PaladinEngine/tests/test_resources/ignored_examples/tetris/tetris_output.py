from stubs.stubs import __ARG__, __AS__, __BMFCS__, __DEF__, __EOLI__, __FC__, __FRAME__, __PIS__, __SOL__, __SOLI__, __UNDEF__


from api.api import PaladinPostCondition
from tests.test_resources.ignored_examples.tetris.graphics import Window, Point, Rectangle, CanvasFrame, Text

class Block(Rectangle):
    """ Block class:
        Implement a block for a tetris piece
        Attributes: x - type: int
                    y - type: int
        specify the position on the tetris board
        in terms of the square grid
    """
    BLOCK_SIZE = 30
    __AS__('BLOCK_SIZE = 30', 'BLOCK_SIZE', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=19)
    OUTLINE_WIDTH = 3
    __AS__('OUTLINE_WIDTH = 3', 'OUTLINE_WIDTH', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=20)

    def __init__(self, pos, color):
        __DEF__('__init__', line_no=22, frame=__FRAME__())
        __PIS__(self, 'self', line_no=22)
        __ARG__('__init__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
        __ARG__('__init__', 'pos', pos, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
        __ARG__('__init__', 'color', color, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
        self.x = pos.x
        __AS__('self.x = pos.x', 'self.x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=23)
        self.y = pos.y
        __AS__('self.y = pos.y', 'self.y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=24)
        self.color = color
        __AS__('self.color = color', 'self.color', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=25)
        p1 = __FC__('Point(pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH, pos.y * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)', Point, locals(), globals(), __FRAME__(), 27, pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH, pos.y * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)
        __AS__('p1 = __FC__(@Point(pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH, pos.y * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)@, Point, locals(), globals(), __FRAME__(), 27, pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH, pos.y * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)', 'p1', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
        p2 = __FC__('Point(p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)', Point, locals(), globals(), __FRAME__(), 29, p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)
        __AS__('p2 = __FC__(@Point(p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)@, Point, locals(), globals(), __FRAME__(), 29, p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)', 'p2', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=29)
        __FC__("__FC__('super(Rectangle, self)', super, locals(), globals(), __FRAME__(), 31, Rectangle, self).__init__(p1, p2)", __FC__('super(Rectangle, self)', super, locals(), globals(), __FRAME__(), 31, Rectangle, self).__init__, locals(), globals(), __FRAME__(), 31, p1, p2)
        __FC__('self.setWidth(Block.OUTLINE_WIDTH)', self.setWidth, locals(), globals(), __FRAME__(), 32, Block.OUTLINE_WIDTH)
        __FC__('self.setFill(color)', self.setFill, locals(), globals(), __FRAME__(), 33, color)
        __UNDEF__('__init__', __FRAME__(), 33)
        return None

    def __repr__(self):
        __DEF__('__repr__', line_no=35, frame=__FRAME__())
        __ARG__('__repr__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=35)
        __UNDEF__('__repr__', __FRAME__(), 36)
        return f'(x, y) = ({self.x},{self.y}), color = {self.color}'

    def can_move(self, board, dx, dy):
        __DEF__('can_move', line_no=38, frame=__FRAME__())
        __ARG__('can_move', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=38)
        __ARG__('can_move', 'board', board, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=38)
        __ARG__('can_move', 'dx', dx, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=38)
        __ARG__('can_move', 'dy', dy, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=38)
        ' Parameters: dx - type: int\n                        dy - type: int\n\n            Return value: type: bool\n\n            checks if the block can move dx squares in the x direction\n            and dy squares in the y direction\n            Returns True if it can, and False otherwise\n            HINT: use the can_move method on the Board object\n        '
        __UNDEF__('can_move', __FRAME__(), 49)
        return __FC__('board.can_move(self.x + dx, self.y + dy)', board.can_move, locals(), globals(), __FRAME__(), 49, self.x + dx, self.y + dy)

    def move(self, dx, dy):
        __DEF__('move', line_no=51, frame=__FRAME__())
        __ARG__('move', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=51)
        __ARG__('move', 'dx', dx, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=51)
        __ARG__('move', 'dy', dy, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=51)
        ' Parameters: dx - type: int\n                        dy - type: int\n\n            moves the block dx squares in the x direction\n            and dy squares in the y direction\n        '
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__0 = self.x + dx
        self.x = ____PALADIN_TEMP_AUG_ASSIGN_VAR__0
        __AS__('self.x = ____PALADIN_TEMP_AUG_ASSIGN_VAR__0', 'self.x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=59)
        ____PALADIN_TEMP_AUG_ASSIGN_VAR__1 = self.y + dy
        self.y = ____PALADIN_TEMP_AUG_ASSIGN_VAR__1
        __AS__('self.y = ____PALADIN_TEMP_AUG_ASSIGN_VAR__1', 'self.y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=60)
        __FC__("__FC__('super(Rectangle, self)', super, locals(), globals(), __FRAME__(), 62, Rectangle, self).move(dx * Block.BLOCK_SIZE, dy * Block.BLOCK_SIZE)", __FC__('super(Rectangle, self)', super, locals(), globals(), __FRAME__(), 62, Rectangle, self).move, locals(), globals(), __FRAME__(), 62, dx * Block.BLOCK_SIZE, dy * Block.BLOCK_SIZE)
        __UNDEF__('move', __FRAME__(), 62)
        return None

    def new_pos_after_rotate(self, dir, center):
        __DEF__('new_pos_after_rotate', line_no=64, frame=__FRAME__())
        __ARG__('new_pos_after_rotate', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=64)
        __ARG__('new_pos_after_rotate', 'dir', dir, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=64)
        __ARG__('new_pos_after_rotate', 'center', center, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=64)
        if self is center:
            __UNDEF__('new_pos_after_rotate', __FRAME__(), 67)
            return (self.x, self.y)
        rot_x = center.x - dir * center.y + dir * self.y
        __AS__('rot_x = center.x - dir * center.y + dir * self.y', 'rot_x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=70)
        rot_y = center.y + dir * center.x - dir * self.x
        __AS__('rot_y = center.y + dir * center.x - dir * self.x', 'rot_y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=71)
        __UNDEF__('new_pos_after_rotate', __FRAME__(), 70)
        return (rot_x, rot_y)

    def __str__(self) -> str:
        return f'B({self.x}, {self.y}, {self.color})'

class Shape(object):
    """ Shape class:
        Base class for all the tetris shapes
        Attributes: blocks - type: list - the list of blocks making up the shape
                    rotation_dir - type: int - the current rotation direction of the shape
                    shift_rotation_dir - type: Boolean - whether or not the shape rotates
    """

    def __init__(self, coords, color):
        self.blocks = []
        __AS__('self.blocks = []', 'self.blocks', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=92)
        self.rotation_dir = 1
        __AS__('self.rotation_dir = 1', 'self.rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=93)
        self.shift_rotation_dir = False
        __AS__('self.shift_rotation_dir = False', 'self.shift_rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=96)
        __SOL__(__FRAME__(), 98)
        for __iter_12 in coords:
            __SOLI__(98, __FRAME__())
            pos = __iter_12
            __AS__('pos = __iter_12', 'pos', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=98)
            __BMFCS__(__FC__('self.blocks.append(Block(pos, color))', self.blocks.append, locals(), globals(), __FRAME__(), 99, Block(pos, color)), self.blocks, 'self.blocks', 'append', 99, __FRAME__(), locals(), globals(), __FC__('Block(pos, color)', Block, locals(), globals(), __FRAME__(), 99, pos, color))
            __EOLI__(__FRAME__(), loop_start_line_no=98, loop_end_line_no=99)
        self.center_block = None
        __AS__('self.center_block = None', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=101)

    def get_blocks(self):
        """returns the list of blocks
        """
        return self.blocks

    def draw(self, win):
        """ Parameter: win - type: CanvasFrame

            Draws the shape:
            i.e. draws each block
        """
        __SOL__(__FRAME__(), 114)
        for __iter_11 in self.blocks:
            __SOLI__(114, __FRAME__())
            block = __iter_11
            __AS__('block = __iter_11', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=114)
            __FC__('block.draw(win)', block.draw, locals(), globals(), __FRAME__(), 115, win)
            __EOLI__(__FRAME__(), loop_start_line_no=114, loop_end_line_no=115)

    def move(self, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            moves the shape dx squares in the x direction
            and dy squares in the y direction, i.e.
            moves each of the blocks
        """
        __SOL__(__FRAME__(), 125)
        for __iter_10 in self.blocks:
            __SOLI__(125, __FRAME__())
            block = __iter_10
            __AS__('block = __iter_10', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=125)
            __FC__('block.move(dx, dy)', block.move, locals(), globals(), __FRAME__(), 126, dx, dy)
            __EOLI__(__FRAME__(), loop_start_line_no=125, loop_end_line_no=126)

    def can_move(self, board, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            Return value: type: bool

            checks if the shape can move dx squares in the x direction
            and dy squares in the y direction, i.e.
            check if each of the blocks can move
            Returns True if all of them can, and False otherwise

        """
        blocks = __FC__('self.get_blocks()', self.get_blocks, locals(), globals(), __FRAME__(), 140)
        __AS__('blocks = __FC__(@self.get_blocks()@, self.get_blocks, locals(), globals(), __FRAME__(), 140)', 'blocks', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=140)
        __SOL__(__FRAME__(), 141)
        for __iter_9 in blocks:
            __SOLI__(141, __FRAME__())
            block = __iter_9
            __AS__('block = __iter_9', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=141)
            if not __FC__('block.can_move(board, dx, dy)', block.can_move, locals(), globals(), __FRAME__(), 142, board, dx, dy):
                return False
            __EOLI__(__FRAME__(), loop_start_line_no=141, loop_end_line_no=143)
        return True

    def get_rotation_dir(self):
        """ Return value: type: int

            returns the current rotation direction
        """
        return self.rotation_dir

    def can_rotate(self, board):
        """ Parameters: board - type: Board object
            Return value: type : bool

            Checks if the shape can be rotated.

            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation and check if
            the new position is valid
            3. If any of the blocks cannot be moved to their new position,
            return False

            otherwise all is good, return True
        """
        rotation_direction = __FC__('self.get_rotation_dir()', self.get_rotation_dir, locals(), globals(), __FRAME__(), 171)
        __AS__('rotation_direction = __FC__(@self.get_rotation_dir()@, self.get_rotation_dir, locals(), globals(), __FRAME__(), 171)', 'rotation_direction', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=171)
        __SOL__(__FRAME__(), 174)
        for __iter_8 in self.blocks:
            __SOLI__(174, __FRAME__())
            block = __iter_8
            __AS__('block = __iter_8', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=174)
            (new_x, new_y) = __FC__('block.new_pos_after_rotate(rotation_direction, self.center_block)', block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 176, rotation_direction, self.center_block)
            __AS__('(new_x, new_y) = __FC__(@block.new_pos_after_rotate(rotation_direction, self.center_block)@, block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 176, rotation_direction, self.center_block)', 'new_y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=176)
            __AS__('(new_x, new_y) = __FC__(@block.new_pos_after_rotate(rotation_direction, self.center_block)@, block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 176, rotation_direction, self.center_block)', 'new_x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=176)
            if not __FC__('board.can_move(new_x, new_y)', board.can_move, locals(), globals(), __FRAME__(), 179, new_x, new_y):
                return False
            __EOLI__(__FRAME__(), loop_start_line_no=174, loop_end_line_no=180)
        return True

    def rotate(self, board):
        """ Parameters: board - type: Board object

            rotates the shape:
            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation
            3. Move the block to the new position

        """
        direction = __FC__('self.get_rotation_dir()', self.get_rotation_dir, locals(), globals(), __FRAME__(), 195)
        __AS__('direction = __FC__(@self.get_rotation_dir()@, self.get_rotation_dir, locals(), globals(), __FRAME__(), 195)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=195)
        __SOL__(__FRAME__(), 198)
        for __iter_7 in self.blocks:
            __SOLI__(198, __FRAME__())
            block = __iter_7
            __AS__('block = __iter_7', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=198)
            (x, y) = __FC__('block.new_pos_after_rotate(direction, self.center_block)', block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 200, direction, self.center_block)
            __AS__('(x, y) = __FC__(@block.new_pos_after_rotate(direction, self.center_block)@, block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 200, direction, self.center_block)', 'y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=200)
            __AS__('(x, y) = __FC__(@block.new_pos_after_rotate(direction, self.center_block)@, block.new_pos_after_rotate, locals(), globals(), __FRAME__(), 200, direction, self.center_block)', 'x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=200)
            __FC__('block.move(dx=x - block.x, dy=y - block.y)', block.move, locals(), globals(), __FRAME__(), 203, dx=x - block.x, dy=y - block.y)
            __EOLI__(__FRAME__(), loop_start_line_no=198, loop_end_line_no=203)
        if self.shift_rotation_dir:
            ____PALADIN_TEMP_AUG_ASSIGN_VAR__2 = self.rotation_dir * -1
            self.rotation_dir = ____PALADIN_TEMP_AUG_ASSIGN_VAR__2
            __AS__('self.rotation_dir = ____PALADIN_TEMP_AUG_ASSIGN_VAR__2', 'self.rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=211)

    def __str__(self):
        return f'{type(self).__qualname__}'

class I_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x - 2, center.y)', Point, locals(), globals(), __FRAME__(), 224, center.x - 2, center.y), __FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 225, center.x - 1, center.y), __FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 226, center.x, center.y), __FC__('Point(center.x + 1, center.y)', Point, locals(), globals(), __FRAME__(), 227, center.x + 1, center.y)]
        __AS__('coords = [__FC__(@Point(center.x - 2, center.y)@, Point, locals(), globals(), __FRAME__(), 224, center.x - 2, center.y), __FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 225, center.x - 1, center.y), __FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 226, center.x, center.y), __FC__(@Point(center.x + 1, center.y)@, Point, locals(), globals(), __FRAME__(), 227, center.x + 1, center.y)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=224)
        __FC__("Shape.__init__(self, coords, 'blue')", Shape.__init__, locals(), globals(), __FRAME__(), 228, self, coords, 'blue')
        self.shift_rotation_dir = True
        __AS__('self.shift_rotation_dir = True', 'self.shift_rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=229)
        self.center_block = self.blocks[2]
        __AS__('self.center_block = self.blocks[2]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=230)

class J_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 235, center.x - 1, center.y), __FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 236, center.x, center.y), __FC__('Point(center.x + 1, center.y)', Point, locals(), globals(), __FRAME__(), 237, center.x + 1, center.y), __FC__('Point(center.x + 1, center.y + 1)', Point, locals(), globals(), __FRAME__(), 238, center.x + 1, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 235, center.x - 1, center.y), __FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 236, center.x, center.y), __FC__(@Point(center.x + 1, center.y)@, Point, locals(), globals(), __FRAME__(), 237, center.x + 1, center.y), __FC__(@Point(center.x + 1, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 238, center.x + 1, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=235)
        __FC__("Shape.__init__(self, coords, 'orange')", Shape.__init__, locals(), globals(), __FRAME__(), 239, self, coords, 'orange')
        self.center_block = self.blocks[1]
        __AS__('self.center_block = self.blocks[1]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=240)

class L_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 245, center.x - 1, center.y), __FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 246, center.x, center.y), __FC__('Point(center.x + 1, center.y)', Point, locals(), globals(), __FRAME__(), 247, center.x + 1, center.y), __FC__('Point(center.x - 1, center.y + 1)', Point, locals(), globals(), __FRAME__(), 248, center.x - 1, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 245, center.x - 1, center.y), __FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 246, center.x, center.y), __FC__(@Point(center.x + 1, center.y)@, Point, locals(), globals(), __FRAME__(), 247, center.x + 1, center.y), __FC__(@Point(center.x - 1, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 248, center.x - 1, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=245)
        __FC__("Shape.__init__(self, coords, 'cyan')", Shape.__init__, locals(), globals(), __FRAME__(), 249, self, coords, 'cyan')
        self.center_block = self.blocks[1]
        __AS__('self.center_block = self.blocks[1]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=250)

class O_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 255, center.x, center.y), __FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 256, center.x - 1, center.y), __FC__('Point(center.x, center.y + 1)', Point, locals(), globals(), __FRAME__(), 257, center.x, center.y + 1), __FC__('Point(center.x - 1, center.y + 1)', Point, locals(), globals(), __FRAME__(), 258, center.x - 1, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 255, center.x, center.y), __FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 256, center.x - 1, center.y), __FC__(@Point(center.x, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 257, center.x, center.y + 1), __FC__(@Point(center.x - 1, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 258, center.x - 1, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=255)
        __FC__("Shape.__init__(self, coords, 'red')", Shape.__init__, locals(), globals(), __FRAME__(), 259, self, coords, 'red')
        self.center_block = self.blocks[0]
        __AS__('self.center_block = self.blocks[0]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=260)

    def rotate(self, board):
        return

class S_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 269, center.x, center.y), __FC__('Point(center.x, center.y + 1)', Point, locals(), globals(), __FRAME__(), 270, center.x, center.y + 1), __FC__('Point(center.x + 1, center.y)', Point, locals(), globals(), __FRAME__(), 271, center.x + 1, center.y), __FC__('Point(center.x - 1, center.y + 1)', Point, locals(), globals(), __FRAME__(), 272, center.x - 1, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 269, center.x, center.y), __FC__(@Point(center.x, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 270, center.x, center.y + 1), __FC__(@Point(center.x + 1, center.y)@, Point, locals(), globals(), __FRAME__(), 271, center.x + 1, center.y), __FC__(@Point(center.x - 1, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 272, center.x - 1, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=269)
        __FC__("Shape.__init__(self, coords, 'green')", Shape.__init__, locals(), globals(), __FRAME__(), 273, self, coords, 'green')
        self.center_block = self.blocks[0]
        __AS__('self.center_block = self.blocks[0]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=274)
        self.shift_rotation_dir = True
        __AS__('self.shift_rotation_dir = True', 'self.shift_rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=275)
        self.rotation_dir = -1
        __AS__('self.rotation_dir = -1', 'self.rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=276)

class T_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 281, center.x - 1, center.y), __FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 282, center.x, center.y), __FC__('Point(center.x + 1, center.y)', Point, locals(), globals(), __FRAME__(), 283, center.x + 1, center.y), __FC__('Point(center.x, center.y + 1)', Point, locals(), globals(), __FRAME__(), 284, center.x, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 281, center.x - 1, center.y), __FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 282, center.x, center.y), __FC__(@Point(center.x + 1, center.y)@, Point, locals(), globals(), __FRAME__(), 283, center.x + 1, center.y), __FC__(@Point(center.x, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 284, center.x, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=281)
        __FC__("Shape.__init__(self, coords, 'yellow')", Shape.__init__, locals(), globals(), __FRAME__(), 285, self, coords, 'yellow')
        self.center_block = self.blocks[1]
        __AS__('self.center_block = self.blocks[1]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=286)

class Z_shape(Shape):

    def __init__(self, center):
        coords = [__FC__('Point(center.x - 1, center.y)', Point, locals(), globals(), __FRAME__(), 291, center.x - 1, center.y), __FC__('Point(center.x, center.y)', Point, locals(), globals(), __FRAME__(), 292, center.x, center.y), __FC__('Point(center.x, center.y + 1)', Point, locals(), globals(), __FRAME__(), 293, center.x, center.y + 1), __FC__('Point(center.x + 1, center.y + 1)', Point, locals(), globals(), __FRAME__(), 294, center.x + 1, center.y + 1)]
        __AS__('coords = [__FC__(@Point(center.x - 1, center.y)@, Point, locals(), globals(), __FRAME__(), 291, center.x - 1, center.y), __FC__(@Point(center.x, center.y)@, Point, locals(), globals(), __FRAME__(), 292, center.x, center.y), __FC__(@Point(center.x, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 293, center.x, center.y + 1), __FC__(@Point(center.x + 1, center.y + 1)@, Point, locals(), globals(), __FRAME__(), 294, center.x + 1, center.y + 1)]', 'coords', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=291)
        __FC__("Shape.__init__(self, coords, 'magenta')", Shape.__init__, locals(), globals(), __FRAME__(), 295, self, coords, 'magenta')
        self.center_block = self.blocks[1]
        __AS__('self.center_block = self.blocks[1]', 'self.center_block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=296)
        self.shift_rotation_dir = True
        __AS__('self.shift_rotation_dir = True', 'self.shift_rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=297)
        self.rotation_dir = -1
        __AS__('self.rotation_dir = -1', 'self.rotation_dir', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=298)

class Board(object):
    """ Board class: it represents the Tetris board

        Attributes: width - type:int - width of the board in squares
                    height - type:int - height of the board in squares
                    canvas - type:CanvasFrame - where the pieces will be drawn
                    grid - type:Dictionary - keeps track of the current state of
                    the board; stores the blocks for a given position
    """

    def __init__(self, win, width, height):
        self.width = width
        __AS__('self.width = width', 'self.width', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=318)
        self.height = height
        __AS__('self.height = height', 'self.height', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=319)
        self.canvas = __FC__('CanvasFrame(win, self.width * Block.BLOCK_SIZE, self.height * Block.BLOCK_SIZE)', CanvasFrame, locals(), globals(), __FRAME__(), 322, win, self.width * Block.BLOCK_SIZE, self.height * Block.BLOCK_SIZE)
        __AS__('self.canvas = __FC__(@CanvasFrame(win, self.width * Block.BLOCK_SIZE, self.height * Block.BLOCK_SIZE)@, CanvasFrame, locals(), globals(), __FRAME__(), 322, win, self.width * Block.BLOCK_SIZE, self.height * Block.BLOCK_SIZE)', 'self.canvas', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=322)
        __FC__("self.canvas.setBackground('light gray')", self.canvas.setBackground, locals(), globals(), __FRAME__(), 324, 'light gray')
        self.grid = {}
        __AS__('self.grid = {}', 'self.grid', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=328)
        self.DEBUG_X = -1
        __AS__('self.DEBUG_X = -1', 'self.DEBUG_X', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=330)
        self.DEBUG_Y = -1
        __AS__('self.DEBUG_Y = -1', 'self.DEBUG_Y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=331)

    def draw_shape(self, shape):
        """ Parameters: shape - type: Shape
            Return value: type: bool

            draws the shape on the board if there is space for it
            and returns True, otherwise it returns False
        """
        if self.DEBUG_X != -1 and self.DEBUG_Y != -1:
            self.grid[self.DEBUG_X, self.DEBUG_Y] = __FC__('shape.get_blocks()', shape.get_blocks, locals(), globals(), __FRAME__(), 342)[0]
            __AS__('self.grid[self.DEBUG_X, self.DEBUG_Y] = __FC__(@shape.get_blocks()@, shape.get_blocks, locals(), globals(), __FRAME__(), 342)[0]', "self.grid['self.DEBUG_X', 'self.DEBUG_Y']", locals=locals(), globals=globals(), frame=__FRAME__(), line_no=342)
        if __FC__('shape.can_move(self, 0, 0)', shape.can_move, locals(), globals(), __FRAME__(), 344, self, 0, 0):
            __FC__('shape.draw(self.canvas)', shape.draw, locals(), globals(), __FRAME__(), 345, self.canvas)
            return True
        return False

    def can_move(self, x, y):
        """ Parameters: x - type:int
                        y - type:int
            Return value: type: bool

            1. check if it is ok to move to square x,y
            if the position is outside of the board boundaries, can't move there
            return False

            2. if there is already a block at that position, can't move there
            return False

            3. otherwise return True

        """
        if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
            return False
        return (x, y) not in self.grid

    def add_shape(self, shape):
        """ Parameter: shape - type:Shape

            add a shape to the grid, i.e.
            add each block to the grid using its
            (x, y) coordinates as a dictionary key

            Hint: use the get_blocks method on Shape to
            get the list of blocks

        """
        blocks = __FC__('shape.get_blocks()', shape.get_blocks, locals(), globals(), __FRAME__(), 383)
        __AS__('blocks = __FC__(@shape.get_blocks()@, shape.get_blocks, locals(), globals(), __FRAME__(), 383)', 'blocks', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=383)
        __SOL__(__FRAME__(), 384)
        for __iter_6 in blocks:
            __SOLI__(384, __FRAME__())
            block = __iter_6
            __AS__('block = __iter_6', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=384)
            self.grid[block.x, block.y] = block
            __AS__('self.grid[block.x, block.y] = block', "self.grid['block.x', 'block.y']", locals=locals(), globals=globals(), frame=__FRAME__(), line_no=385)
            __EOLI__(__FRAME__(), loop_start_line_no=384, loop_end_line_no=385)

    def row(self, y):
        extracted_row = []
        __AS__('extracted_row = []', 'extracted_row', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=390)
        __SOL__(__FRAME__(), 391)
        for __iter_5 in self.grid:
            __SOLI__(391, __FRAME__())
            block = __iter_5
            __AS__('block = __iter_5', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=391)
            if block[1] == y:
                __BMFCS__(__FC__('extracted_row.append(block)', extracted_row.append, locals(), globals(), __FRAME__(), 393, block), extracted_row, 'extracted_row', 'append', 393, __FRAME__(), locals(), globals(), block)
            __EOLI__(__FRAME__(), loop_start_line_no=391, loop_end_line_no=393)
        return extracted_row

    @__FC__("PaladinPostCondition('never exists row(board, y)')", PaladinPostCondition, locals(), globals(), __FRAME__(), 397, 'never exists row(board, y)')
    def delete_row(self, y):
        """
            Parameters: y - type:int

            remove all the blocks in row y
            to remove a block you must remove it from the grid
            and erase it from the screen.
            If you don't remember how to erase a graphics object
            from the screen, take a look at the Graphics Library
            handout

        """
        grid_blocks_keys = __FC__("__FC__('self.grid.copy()', self.grid.copy, locals(), globals(), __FRAME__(), 412).keys()", __FC__('self.grid.copy()', self.grid.copy, locals(), globals(), __FRAME__(), 412).keys, locals(), globals(), __FRAME__(), 412)
        __AS__('grid_blocks_keys = __FC__(@__FC__(@self.grid.copy()@, self.grid.copy, locals(), globals(), __FRAME__(), 412).keys()@, __FC__(@self.grid.copy()@, self.grid.copy, locals(), globals(), __FRAME__(), 412).keys, locals(), globals(), __FRAME__(), 412)', 'grid_blocks_keys', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=412)
        __SOL__(__FRAME__(), 413)
        for __iter_4 in __FC__('filter(lambda k: k[1] == y, grid_blocks_keys)', filter, locals(), globals(), __FRAME__(), 413, lambda k: k[1] == y, grid_blocks_keys):
            __SOLI__(413, __FRAME__())
            (_x, _y) = __iter_4
            __AS__('(_x, _y) = __iter_4', '_y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=413)
            __AS__('(_x, _y) = __iter_4', '_x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=413)
            __FC__('self.grid[_x, _y].undraw()', self.grid[_x, _y].undraw, locals(), globals(), __FRAME__(), 415)
            del self.grid[_x, _y]
            self.DEBUG_X = _x
            __AS__('self.DEBUG_X = _x', 'self.DEBUG_X', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=420)
            self.DEBUG_Y = _y
            __AS__('self.DEBUG_Y = _y', 'self.DEBUG_Y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=421)
            __EOLI__(__FRAME__(), loop_start_line_no=413, loop_end_line_no=421)

    def is_row_complete(self, y):
        """ Parameter: y - type: int
            Return value: type: bool

            for each block in row y
            check if there is a block in the grid (use the in operator)
            if there is one square that is not occupied, return False
            otherwise return True

        """
        r = __FC__('range(0, self.width)', range, locals(), globals(), __FRAME__(), 433, 0, self.width)
        __AS__('r = __FC__(@range(0, self.width)@, range, locals(), globals(), __FRAME__(), 433, 0, self.width)', 'r', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=433)
        return __FC__('all(((x, y) in self.grid for x in r))', all, locals(), globals(), __FRAME__(), 434, ((x, y) in self.grid for x in r))

    def move_down_rows(self, y_start):
        """ Parameters: y_start - type:int

            for each row from y_start to the top
                for each column
                    check if there is a block in the grid
                    if there is, remove it from the grid
                    and move the block object down on the screen
                    and then place it back in the grid in the new position

        """
        r = __FC__('range(0, y_start)', range, locals(), globals(), __FRAME__(), 447, 0, y_start)
        __AS__('r = __FC__(@range(0, y_start)@, range, locals(), globals(), __FRAME__(), 447, 0, y_start)', 'r', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=447)
        __SOL__(__FRAME__(), 448)
        for __iter_3 in r:
            __SOLI__(448, __FRAME__())
            k = __iter_3
            __AS__('k = __iter_3', 'k', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=448)
            y = y_start - k
            __AS__('y = y_start - k', 'y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=449)
            __SOL__(__FRAME__(), 450)
            for __iter_2 in [_x for (_x, _y) in self.grid if _y == y]:
                __SOLI__(450, __FRAME__())
                x = __iter_2
                __AS__('x = __iter_2', 'x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=450)
                block = __BMFCS__(__FC__('self.grid.pop((x, y))', self.grid.pop, locals(), globals(), __FRAME__(), 452, (x, y)), self.grid, 'self.grid', 'pop', 452, __FRAME__(), locals(), globals(), (x, y))
                __AS__('block = __BMFCS__(__FC__(@self.grid.pop((x, y))@, self.grid.pop, locals(), globals(), __FRAME__(), 452, (x, y)), self.grid, @self.grid@, @pop@, 452, __FRAME__(), locals(), globals(), (x, y))', 'block', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=452)
                __FC__('block.move(0, 1)', block.move, locals(), globals(), __FRAME__(), 453, 0, 1)
                __EOLI__(__FRAME__(), loop_start_line_no=450, loop_end_line_no=453)
            __EOLI__(__FRAME__(), loop_start_line_no=448, loop_end_line_no=453)

    def remove_complete_rows(self):
        """ removes all the complete rows
            1. for each row, y,
            2. check if the row is complete
                if it is,
                    delete the row
                    move all rows down starting at row y - 1

        """
        r = 1
        __AS__('r = 1', 'r', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=466)
        __SOL__(__FRAME__(), 467)
        while r < self.height:
            __SOLI__(467, __FRAME__())
            y = self.height - r
            __AS__('y = self.height - r', 'y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=468)
            if __FC__('self.is_row_complete(y)', self.is_row_complete, locals(), globals(), __FRAME__(), 469, y):
                __FC__('self.delete_row(y)', self.delete_row, locals(), globals(), __FRAME__(), 471, y)
                __FC__('self.move_down_rows(y - 1)', self.move_down_rows, locals(), globals(), __FRAME__(), 474, y - 1)
                ____PALADIN_TEMP_AUG_ASSIGN_VAR__4 = r - 1
                r = ____PALADIN_TEMP_AUG_ASSIGN_VAR__4
                __AS__('r = ____PALADIN_TEMP_AUG_ASSIGN_VAR__4', 'r', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=475)
            ____PALADIN_TEMP_AUG_ASSIGN_VAR__3 = r + 1
            r = ____PALADIN_TEMP_AUG_ASSIGN_VAR__3
            __AS__('r = ____PALADIN_TEMP_AUG_ASSIGN_VAR__3', 'r', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=476)
            __EOLI__(__FRAME__(), loop_start_line_no=467, loop_end_line_no=476)

    def game_over(self):
        """ display "Game Over !!!" message in the center of the board
            HINT: use the Text class from the graphics library
        """
        w = __FC__('int(self.width / 2)', int, locals(), globals(), __FRAME__(), 482, self.width / 2)
        __AS__('w = __FC__(@int(self.width / 2)@, int, locals(), globals(), __FRAME__(), 482, self.width / 2)', 'w', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=482)
        h = __FC__('int(self.height / 2)', int, locals(), globals(), __FRAME__(), 483, self.height / 2)
        __AS__('h = __FC__(@int(self.height / 2)@, int, locals(), globals(), __FRAME__(), 483, self.height / 2)', 'h', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=483)
        p = __FC__('Point(w, h)', Point, locals(), globals(), __FRAME__(), 484, w, h)
        __AS__('p = __FC__(@Point(w, h)@, Point, locals(), globals(), __FRAME__(), 484, w, h)', 'p', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=484)
        text = __FC__("Text(p, 'Game Over !!!')", Text, locals(), globals(), __FRAME__(), 485, p, 'Game Over !!!')
        __AS__('text = __FC__(@Text(p, @Game Over !!!@)@, Text, locals(), globals(), __FRAME__(), 485, p, @Game Over !!!@)', 'text', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=485)
        __FC__('text.draw(self.canvas)', text.draw, locals(), globals(), __FRAME__(), 486, self.canvas)
        __FC__('win.destroy()', win.destroy, locals(), globals(), __FRAME__(), 487)

    def __str__(self):
        return f'Board({id(self)}): {[(x, y) for (x, y) in self.grid]}'

class Tetris(object):
    """ Tetris class: Controls the game play
        Attributes:
            SHAPES - type: list (list of Shape classes)
            DIRECTION - type: dictionary - converts string direction to (dx, dy)
            BOARD_WIDTH - type:int - the width of the board
            BOARD_HEIGHT - type:int - the height of the board
            board - type:Board - the tetris board
            win - type:Window - the window for the tetris game
            delay - type:int - the speed in milliseconds for moving the shapes
            current_shapes - type: Shape - the current moving shape on the board
    """
    SHAPES = [I_shape, J_shape, L_shape, O_shape, S_shape, T_shape, Z_shape]
    __AS__('SHAPES = [I_shape, J_shape, L_shape, O_shape, S_shape, T_shape, Z_shape]', 'SHAPES', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=512)
    DIRECTION = {'Left': (-1, 0), 'Right': (1, 0), 'Down': (0, 1)}
    __AS__('DIRECTION = {@Left@: (-1, 0), @Right@: (1, 0), @Down@: (0, 1)}', 'DIRECTION', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=513)
    BOARD_WIDTH = 10
    __AS__('BOARD_WIDTH = 10', 'BOARD_WIDTH', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=514)
    BOARD_HEIGHT = 20
    __AS__('BOARD_HEIGHT = 20', 'BOARD_HEIGHT', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=515)
    TEST_MODE = True
    __AS__('TEST_MODE = True', 'TEST_MODE', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=516)

    def __init__(self, win):
        self.board = __FC__('Board(win, self.BOARD_WIDTH, self.BOARD_HEIGHT)', Board, locals(), globals(), __FRAME__(), 519, win, self.BOARD_WIDTH, self.BOARD_HEIGHT)
        __AS__('self.board = __FC__(@Board(win, self.BOARD_WIDTH, self.BOARD_HEIGHT)@, Board, locals(), globals(), __FRAME__(), 519, win, self.BOARD_WIDTH, self.BOARD_HEIGHT)', 'self.board', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=519)
        self.win = win
        __AS__('self.win = win', 'self.win', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=520)
        self.delay = 500
        __AS__('self.delay = 500', 'self.delay', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=521)
        self.TEST_MOCK_COUNTER_X = -1
        __AS__('self.TEST_MOCK_COUNTER_X = -1', 'self.TEST_MOCK_COUNTER_X', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=523)
        self.TEST_MOCK_COUNTER_Y = self.BOARD_HEIGHT - 2
        __AS__('self.TEST_MOCK_COUNTER_Y = self.BOARD_HEIGHT - 2', 'self.TEST_MOCK_COUNTER_Y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=524)
        __FC__("self.win.bind_all('<Key>', self.key_pressed)", self.win.bind_all, locals(), globals(), __FRAME__(), 528, '<Key>', self.key_pressed)
        self.current_shape = __FC__('self.create_new_shape()', self.create_new_shape, locals(), globals(), __FRAME__(), 531)
        __AS__('self.current_shape = __FC__(@self.create_new_shape()@, self.create_new_shape, locals(), globals(), __FRAME__(), 531)', 'self.current_shape', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=531)
        __FC__('self.board.draw_shape(self.current_shape)', self.board.draw_shape, locals(), globals(), __FRAME__(), 535, self.current_shape)
        __FC__('self.animate_shape()', self.animate_shape, locals(), globals(), __FRAME__(), 538)

    def create_new_shape(self):
        """ Return value: type: Shape

            Create a random new shape that is centered
             at y = 0 and x = int(self.BOARD_WIDTH/2)
            return the shape
        """
        return __FC__('O_shape(Point(self.BOARD_WIDTH / 2, y=0))', O_shape, locals(), globals(), __FRAME__(), 550, Point(self.BOARD_WIDTH / 2, y=0))

    def animate_shape(self):
        """ animate the shape - move down at equal intervals
            specified by the delay attribute
        """
        next_move = __FC__("self.do_move('Down')", self.do_move, locals(), globals(), __FRAME__(), 557, 'Down')
        __AS__('next_move = __FC__(@self.do_move(@Down@)@, self.do_move, locals(), globals(), __FRAME__(), 557, @Down@)', 'next_move', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=557)
        if next_move:
            __FC__('self.win.after(self.delay, self.animate_shape)', self.win.after, locals(), globals(), __FRAME__(), 559, self.delay, self.animate_shape)
        else:
            return

    def do_move(self, direction):
        """ Parameters: direction - type: string
            Return value: type: bool

            Move the current shape in the direction specified by the parameter:
            First check if the shape can move. If it can, move it and return True
            Otherwise if the direction we tried to move was 'Down',
            1. add the current shape to the board
            2. remove the completed rows if any
            3. create a new random shape and set current_shape attribute
            4. If the shape cannot be drawn on the board, display a
               game over message

            return False

        """
        (dx, dy) = self.DIRECTION[direction]
        __AS__('(dx, dy) = self.DIRECTION[direction]', 'dy', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=580)
        __AS__('(dx, dy) = self.DIRECTION[direction]', 'dx', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=580)
        if __FC__('self.current_shape.can_move(self.board, dx, dy)', self.current_shape.can_move, locals(), globals(), __FRAME__(), 583, self.board, dx, dy):
            __FC__('self.current_shape.move(dx, dy)', self.current_shape.move, locals(), globals(), __FRAME__(), 585, dx, dy)
            return True
        if direction != 'Down':
            return False
        __FC__('self.board.add_shape(self.current_shape)', self.board.add_shape, locals(), globals(), __FRAME__(), 594, self.current_shape)
        __FC__('self.board.remove_complete_rows()', self.board.remove_complete_rows, locals(), globals(), __FRAME__(), 597)
        self.current_shape = __FC__('self.create_new_shape()', self.create_new_shape, locals(), globals(), __FRAME__(), 600)
        __AS__('self.current_shape = __FC__(@self.create_new_shape()@, self.create_new_shape, locals(), globals(), __FRAME__(), 600)', 'self.current_shape', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=600)
        if not __FC__('self.board.draw_shape(self.current_shape)', self.board.draw_shape, locals(), globals(), __FRAME__(), 603, self.current_shape):
            __FC__('self.board.game_over()', self.board.game_over, locals(), globals(), __FRAME__(), 605)
            return False
        return True

    def do_rotate(self):
        """ Checks if the current_shape can be rotated and
            rotates if it can
        """
        if __FC__('self.current_shape.can_rotate(self.board)', self.current_shape.can_rotate, locals(), globals(), __FRAME__(), 615, self.board):
            __FC__('self.current_shape.rotate(self.board)', self.current_shape.rotate, locals(), globals(), __FRAME__(), 616, self.board)

    def key_pressed(self, event):
        """ this function is called when a key is pressed on the keyboard
            it currenly just prints the value of the key

            Modify the function so that if the user presses the arrow keys
            'Left', 'Right' or 'Down', the current_shape will move in
            the appropriate direction

            if the user presses the space bar 'space', the shape will move
            down until it can no longer move and is added to the board

            if the user presses the 'Up' arrow key ,
                the shape should rotate.

        """
        key = event.keysym
        __AS__('key = event.keysym', 'key', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=633)
        if key in self.DIRECTION:
            __FC__('self.do_move(key)', self.do_move, locals(), globals(), __FRAME__(), 636, key)
        elif key == 'space':
            shape_going_down = self.current_shape
            __AS__('shape_going_down = self.current_shape', 'shape_going_down', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=639)
            __SOL__(__FRAME__(), 640)
            while __FC__("self.do_move('Down')", self.do_move, locals(), globals(), __FRAME__(), 640, 'Down'):
                __SOLI__(640, __FRAME__())
                if shape_going_down is not self.current_shape:
                    break
                __EOLI__(__FRAME__(), loop_start_line_no=640, loop_end_line_no=642)
        elif key == 'Up':
            __FC__('self.do_rotate()', self.do_rotate, locals(), globals(), __FRAME__(), 645)
        if key == 'Q' or key == 'q':
            __FC__('self.board.game_over()', self.board.game_over, locals(), globals(), __FRAME__(), 649)
if __name__ == '__main__':
    win = __FC__("Window('Tetris')", Window, locals(), globals(), __FRAME__(), 656, 'Tetris')
    __AS__('win = __FC__(@Window(@Tetris@)@, Window, locals(), globals(), __FRAME__(), 656, @Tetris@)', 'win', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=656)
    game = __FC__('Tetris(win)', Tetris, locals(), globals(), __FRAME__(), 657, win)
    __AS__('game = __FC__(@Tetris(win)@, Tetris, locals(), globals(), __FRAME__(), 657, win)', 'game', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=657)
    __FC__('win.mainloop()', win.mainloop, locals(), globals(), __FRAME__(), 658)