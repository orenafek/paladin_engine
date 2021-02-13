import random
from Examples.Tetris.graphics import Window, Point, Rectangle, CanvasFrame, Text
from engine import __AS__


class Block(Rectangle):
    """ Block class:
        Implement a block for a tetris piece
        Attributes: x - type: int
                    y - type: int
        specify the position on the tetris board
        in terms of the square grid
    """
    BLOCK_SIZE = 30
    __AS__(('BLOCK_SIZE', BLOCK_SIZE), locals=locals(), globals=globals())
    OUTLINE_WIDTH = 3
    __AS__(('OUTLINE_WIDTH', OUTLINE_WIDTH), locals=locals(), globals=globals()
        )

    def __init__(self, pos, color):
        self.x = pos.x
        __AS__(('self', self), locals=locals(), globals=globals())
        self.y = pos.y
        __AS__(('self', self), locals=locals(), globals=globals())
        self.color = color
        __AS__(('self', self), locals=locals(), globals=globals())
        p1 = Point(pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH, pos.y *
            Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)
        __AS__(('p1', p1), locals=locals(), globals=globals())
        p2 = Point(p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)
        __AS__(('p2', p2), locals=locals(), globals=globals())
        Rectangle.__init__(self, p1, p2)
        self.setWidth(Block.OUTLINE_WIDTH)
        self.setFill(color)

    def can_move(self, board, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            Return value: type: bool

            checks if the block can move dx squares in the x direction
            and dy squares in the y direction
            Returns True if it can, and False otherwise
            HINT: use the can_move method on the Board object
        """
        return board.can_move(self.x + dx, self.y + dy)

    def move(self, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            moves the block dx squares in the x direction
            and dy squares in the y direction
        """
        self.x += dx
        self.y += dy
        Rectangle.move(self, dx * Block.BLOCK_SIZE, dy * Block.BLOCK_SIZE)

    def new_pos_after_rotate(self, dir, center):
        if self is center:
            return self.x, self.y
        rot_x = center.x - dir * center.y + dir * self.y
        __AS__(('rot_x', rot_x), locals=locals(), globals=globals())
        rot_y = center.y + dir * center.x - dir * self.x
        __AS__(('rot_y', rot_y), locals=locals(), globals=globals())
        return rot_x, rot_y

    def __str__(self) ->str:
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
        __AS__(('self', self), locals=locals(), globals=globals())
        self.rotation_dir = 1
        __AS__(('self', self), locals=locals(), globals=globals())
        self.shift_rotation_dir = False
        __AS__(('self', self), locals=locals(), globals=globals())
        for pos in coords:
            self.blocks.append(Block(pos, color))
        self.center_block = None
        __AS__(('self', self), locals=locals(), globals=globals())

    def get_blocks(self):
        """returns the list of blocks
        """
        return self.blocks

    def draw(self, win):
        """ Parameter: win - type: CanvasFrame

            Draws the shape:
            i.e. draws each block
        """
        for block in self.blocks:
            block.draw(win)

    def move(self, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            moves the shape dx squares in the x direction
            and dy squares in the y direction, i.e.
            moves each of the blocks
        """
        for block in self.blocks:
            block.move(dx, dy)

    def can_move(self, board, dx, dy):
        """ Parameters: dx - type: int
                        dy - type: int

            Return value: type: bool

            checks if the shape can move dx squares in the x direction
            and dy squares in the y direction, i.e.
            check if each of the blocks can move
            Returns True if all of them can, and False otherwise

        """
        return all(block.can_move(board, dx, dy) for block in self.get_blocks()
            )

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
        rotation_direction = self.get_rotation_dir()
        __AS__(('rotation_direction', rotation_direction), locals=locals(),
            globals=globals())
        for block in self.blocks:
            new_x, new_y = block.new_pos_after_rotate(rotation_direction,
                self.center_block)
            __AS__(('new_x', new_x), ('new_y', new_y), locals=locals(),
                globals=globals())
            if not board.can_move(new_x, new_y):
                return False
        return True

    def rotate(self, board):
        """ Parameters: board - type: Board object

            rotates the shape:
            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation
            3. Move the block to the new position

        """
        direction = self.get_rotation_dir()
        __AS__(('direction', direction), locals=locals(), globals=globals())
        for block in self.blocks:
            x, y = block.new_pos_after_rotate(direction, self.center_block)
            __AS__(('x', x), ('y', y), locals=locals(), globals=globals())
            block.move(dx=x - block.x, dy=y - block.y)
        if self.shift_rotation_dir:
            self.rotation_dir *= -1

    def __str__(self):
        return f'{type(self).__qualname__}'


class I_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x - 2, center.y), Point(center.x - 1, center
            .y), Point(center.x, center.y), Point(center.x + 1, center.y)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'blue')
        self.shift_rotation_dir = True
        __AS__(('self', self), locals=locals(), globals=globals())
        self.center_block = self.blocks[2]
        __AS__(('self', self), locals=locals(), globals=globals())


class J_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x - 1, center.y), Point(center.x, center.y),
            Point(center.x + 1, center.y), Point(center.x + 1, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'orange')
        self.center_block = self.blocks[1]
        __AS__(('self', self), locals=locals(), globals=globals())


class L_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x - 1, center.y), Point(center.x, center.y),
            Point(center.x + 1, center.y), Point(center.x - 1, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'cyan')
        self.center_block = self.blocks[1]
        __AS__(('self', self), locals=locals(), globals=globals())


class O_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x, center.y), Point(center.x - 1, center.y),
            Point(center.x, center.y + 1), Point(center.x - 1, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'red')
        self.center_block = self.blocks[0]
        __AS__(('self', self), locals=locals(), globals=globals())

    def rotate(self, board):
        return


class S_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x, center.y), Point(center.x, center.y + 1),
            Point(center.x + 1, center.y), Point(center.x - 1, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'green')
        self.center_block = self.blocks[0]
        __AS__(('self', self), locals=locals(), globals=globals())
        self.shift_rotation_dir = True
        __AS__(('self', self), locals=locals(), globals=globals())
        self.rotation_dir = -1
        __AS__(('self', self), locals=locals(), globals=globals())


class T_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x - 1, center.y), Point(center.x, center.y),
            Point(center.x + 1, center.y), Point(center.x, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'yellow')
        self.center_block = self.blocks[1]
        __AS__(('self', self), locals=locals(), globals=globals())


class Z_shape(Shape):

    def __init__(self, center):
        coords = [Point(center.x - 1, center.y), Point(center.x, center.y),
            Point(center.x, center.y + 1), Point(center.x + 1, center.y + 1)]
        __AS__(('coords', coords), locals=locals(), globals=globals())
        Shape.__init__(self, coords, 'magenta')
        self.center_block = self.blocks[1]
        __AS__(('self', self), locals=locals(), globals=globals())
        self.shift_rotation_dir = True
        __AS__(('self', self), locals=locals(), globals=globals())
        self.rotation_dir = -1
        __AS__(('self', self), locals=locals(), globals=globals())


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
        __AS__(('self', self), locals=locals(), globals=globals())
        self.height = height
        __AS__(('self', self), locals=locals(), globals=globals())
        self.canvas = CanvasFrame(win, self.width * Block.BLOCK_SIZE, self.
            height * Block.BLOCK_SIZE)
        __AS__(('self', self), locals=locals(), globals=globals())
        self.canvas.setBackground('light gray')
        self.grid = {}
        __AS__(('self', self), locals=locals(), globals=globals())

    def draw_shape(self, shape):
        """ Parameters: shape - type: Shape
            Return value: type: bool

            draws the shape on the board if there is space for it
            and returns True, otherwise it returns False
        """
        if shape.can_move(self, 0, 0):
            shape.draw(self.canvas)
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
        for block in shape.get_blocks():
            self.grid[block.x, block.y] = block
            __AS__(('self', self), ('block', block), ('block', block),
                locals=locals(), globals=globals())

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
        for _x, _y in filter(lambda k: k[1] == y, self.grid.keys()):
            self.grid[_x, _y].undraw()
            del self.grid[_x, _y]

    def is_row_complete(self, y):
        """ Parameter: y - type: int
            Return value: type: bool

            for each block in row y
            check if there is a block in the grid (use the in operator)
            if there is one square that is not occupied, return False
            otherwise return True

        """
        return all((x, y) in self.grid for x in range(0, self.width))

    def move_down_rows(self, y_start):
        """ Parameters: y_start - type:int

            for each row from y_start to the top
                for each column
                    check if there is a block in the grid
                    if there is, remove it from the grid
                    and move the block object down on the screen
                    and then place it back in the grid in the new position

        """
        print('reversed(range(0, y_start)) = ', list(reversed(range(0,
            y_start))))
        for y in reversed(range(0, y_start)):
            for x in [_x for _x, _y in self.grid if _y == y]:
                block = self.grid.pop((x, y))
                __AS__(('block', block), locals=locals(), globals=globals())
                if block.can_move(self, x, y):
                    print('Moving ({}, {})'.format(x, y))
                    block.move(0, 1)
                print('After move: block.x, block.y', block.x, ', ', block.y)
                self.grid[x, y + 1] = block
                __AS__(('self', self), ('x', x), ('y', y), locals=locals(),
                    globals=globals())

    def remove_complete_rows(self):
        """ removes all the complete rows
            1. for each row, y,
            2. check if the row is complete
                if it is,
                    delete the row
                    move all rows down starting at row y - 1

        """
        for y in range(0, self.height):
            if self.is_row_complete(y):
                self.delete_row(y)
                self.move_down_rows(y - 1)

    def game_over(self):
        """ display "Game Over !!!" message in the center of the board
            HINT: use the Text class from the graphics library
        """
        Text(Point(int(self.width / 2), int(self.height / 2)), 'Game Over !!!'
            ).draw(self.canvas)


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
    __AS__(('SHAPES', SHAPES), locals=locals(), globals=globals())
    DIRECTION = {'Left': (-1, 0), 'Right': (1, 0), 'Down': (0, 1)}
    __AS__(('DIRECTION', DIRECTION), locals=locals(), globals=globals())
    BOARD_WIDTH = 10
    __AS__(('BOARD_WIDTH', BOARD_WIDTH), locals=locals(), globals=globals())
    BOARD_HEIGHT = 20
    __AS__(('BOARD_HEIGHT', BOARD_HEIGHT), locals=locals(), globals=globals())

    def __init__(self, win):
        self.board = Board(win, self.BOARD_WIDTH, self.BOARD_HEIGHT)
        __AS__(('self', self), locals=locals(), globals=globals())
        self.win = win
        __AS__(('self', self), locals=locals(), globals=globals())
        self.delay = 1000
        __AS__(('self', self), locals=locals(), globals=globals())
        self.win.bind_all('<Key>', self.key_pressed)
        self.current_shape = self.create_new_shape()
        __AS__(('self', self), locals=locals(), globals=globals())
        self.board.draw_shape(self.current_shape)
        self.animate_shape()

    def create_new_shape(self):
        """ Return value: type: Shape

            Create a random new shape that is centered
             at y = 0 and x = int(self.BOARD_WIDTH/2)
            return the shape
        """
        shape_class = random.choice(Shape.__subclasses__())
        __AS__(('shape_class', shape_class), locals=locals(), globals=globals()
            )
        return shape_class(Point(x=int(self.BOARD_WIDTH / 2), y=0))

    def animate_shape(self):
        """ animate the shape - move down at equal intervals
            specified by the delay attribute
        """
        next_move = self.do_move('Down')
        __AS__(('next_move', next_move), locals=locals(), globals=globals())
        if next_move:
            self.win.after(self.delay, self.animate_shape)
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
        dx, dy = self.DIRECTION[direction]
        __AS__(('dx', dx), ('dy', dy), locals=locals(), globals=globals())
        if self.current_shape.can_move(self.board, dx, dy):
            self.current_shape.move(dx, dy)
            return True
        if direction != 'Down':
            return False
        self.board.add_shape(self.current_shape)
        self.board.remove_complete_rows()
        self.current_shape = self.create_new_shape()
        __AS__(('self', self), locals=locals(), globals=globals())
        if not self.board.draw_shape(self.current_shape):
            self.board.game_over()
            return False
        return True

    def do_rotate(self):
        """ Checks if the current_shape can be rotated and
            rotates if it can
        """
        if self.current_shape.can_rotate(self.board):
            self.current_shape.rotate(self.board)

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
        __AS__(('key', key), locals=locals(), globals=globals())
        if key in self.DIRECTION:
            self.do_move(key)
        elif key == 'space':
            shape_going_down = self.current_shape
            __AS__(('shape_going_down', shape_going_down), locals=locals(),
                globals=globals())
            while self.do_move('Down'):
                if shape_going_down is not self.current_shape:
                    break
        elif key == 'Up':
            self.do_rotate()


if __name__ == '__main__':
    ishape = I_shape(Point(1, 2))
    win = Window('Tetris')
    __AS__(('win', win), locals=locals(), globals=globals())
    game = Tetris(win)
    __AS__(('game', game), locals=locals(), globals=globals())
    win.mainloop()

    from engine import archive
    print(archive)
