import random

from Examples.Tetris.graphics import Window, Point, Rectangle, CanvasFrame, Text

############################################################
# BLOCK CLASS
############################################################
from api.api import Paladinize, PaladinPostCondition, Paladin

Paladin.pause_record()

class Block(Rectangle):
    ''' Block class:
        Implement a block for a tetris piece
        Attributes: x - type: int
                    y - type: int
        specify the position on the tetris board
        in terms of the square grid
    '''

    BLOCK_SIZE = 30
    OUTLINE_WIDTH = 3

    def __init__(self, pos, color):
        self.x = pos.x
        self.y = pos.y
        self.color = color

        p1 = Point(pos.x * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH,
                   pos.y * Block.BLOCK_SIZE + Block.OUTLINE_WIDTH)
        p2 = Point(p1.x + Block.BLOCK_SIZE, p1.y + Block.BLOCK_SIZE)

        Rectangle.__init__(self, p1, p2)
        self.setWidth(Block.OUTLINE_WIDTH)
        self.setFill(color)

    def __repr__(self):
        return f'(x, y) = ({self.x},{self.y}), color = {self.color}'

    def can_move(self, board, dx, dy):
        ''' Parameters: dx - type: int
                        dy - type: int

            Return value: type: bool

            checks if the block can move dx squares in the x direction
            and dy squares in the y direction
            Returns True if it can, and False otherwise
            HINT: use the can_move method on the Board object
        '''
        return board.can_move(self.x + dx, self.y + dy)

    def move(self, dx, dy):
        ''' Parameters: dx - type: int
                        dy - type: int

            moves the block dx squares in the x direction
            and dy squares in the y direction
        '''

        self.x += dx
        self.y += dy

        Rectangle.move(self, dx * Block.BLOCK_SIZE, dy * Block.BLOCK_SIZE)

    def new_pos_after_rotate(self, dir, center):
        if self is center:
            # Rotating a block around itself does nothing.
            return self.x, self.y

        # Calculate rotated x.
        rot_x = center.x - dir * center.y + dir * self.y
        rot_y = center.y + dir * center.x - dir * self.x

        return rot_x, rot_y

    def __str__(self) -> str:
        return f'B({self.x}, {self.y}, {self.color})'


############################################################
# SHAPE CLASS
############################################################

class Shape(object):
    ''' Shape class:
        Base class for all the tetris shapes
        Attributes: blocks - type: list - the list of blocks making up the shape
                    rotation_dir - type: int - the current rotation direction of the shape
                    shift_rotation_dir - type: Boolean - whether or not the shape rotates
    '''

    def __init__(self, coords, color):
        self.blocks = []
        self.rotation_dir = 1
        ### A boolean to indicate if a shape shifts rotation direction or not.
        ### Defaults to false since only 3 shapes shift rotation directions (I, S and Z)
        self.shift_rotation_dir = False

        for pos in coords:
            self.blocks.append(Block(pos, color))

        self.center_block = None

    def get_blocks(self):
        '''returns the list of blocks
        '''
        return self.blocks

    def draw(self, win):
        ''' Parameter: win - type: CanvasFrame

            Draws the shape:
            i.e. draws each block
        '''
        for block in self.blocks:
            block.draw(win)

    def move(self, dx, dy):
        ''' Parameters: dx - type: int
                        dy - type: int

            moves the shape dx squares in the x direction
            and dy squares in the y direction, i.e.
            moves each of the blocks
        '''
        for block in self.blocks:
            block.move(dx, dy)

    def can_move(self, board, dx, dy):
        ''' Parameters: dx - type: int
                        dy - type: int

            Return value: type: bool

            checks if the shape can move dx squares in the x direction
            and dy squares in the y direction, i.e.
            check if each of the blocks can move
            Returns True if all of them can, and False otherwise

        '''
        blocks = self.get_blocks()
        for block in blocks:
            if not block.can_move(board, dx, dy):
                return False
        return True

        # return all(block.can_move(board, dx, dy) for block in self.get_blocks())

    def get_rotation_dir(self):
        ''' Return value: type: int

            returns the current rotation direction
        '''
        return self.rotation_dir

    def can_rotate(self, board):
        ''' Parameters: board - type: Board object
            Return value: type : bool

            Checks if the shape can be rotated.

            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation and check if
            the new position is valid
            3. If any of the blocks cannot be moved to their new position,
            return False

            otherwise all is good, return True
        '''

        # Get rotation direction.
        rotation_direction = self.get_rotation_dir()

        # For all blocks in the shape:
        for block in self.blocks:
            # Calculate new position after rotation.
            new_x, new_y = block.new_pos_after_rotate(rotation_direction, self.center_block)

            # Check if the block can be moved there.
            if not board.can_move(new_x, new_y):
                return False

        return True

    def rotate(self, board):
        ''' Parameters: board - type: Board object

            rotates the shape:
            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation
            3. Move the block to the new position

        '''

        # Get rotation direction.
        direction = self.get_rotation_dir()

        # Go over each block in the shape:
        for block in self.blocks:
            # Calculate new position after rotate.
            x, y = block.new_pos_after_rotate(direction, self.center_block)

            # Move the block.
            block.move(dx=x - block.x, dy=y - block.y)

        ### This should be at the END of your rotate code.
        ### DO NOT touch it. Default behavior is that a piece will only shift
        ### rotation direciton after a successful rotation. This ensures that
        ### pieces which switch rotations definitely remain within their
        ### accepted rotation positions.
        if self.shift_rotation_dir:
            self.rotation_dir *= -1

    def __str__(self):
        return f'{Shape.__qualname__}'


############################################################
# ALL SHAPE CLASSES
############################################################


class I_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 2, center.y),
                  Point(center.x - 1, center.y),
                  Point(center.x, center.y),
                  Point(center.x + 1, center.y)]
        Shape.__init__(self, coords, 'blue')
        self.shift_rotation_dir = True
        self.center_block = self.blocks[2]


class J_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x, center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x + 1, center.y + 1)]
        Shape.__init__(self, coords, 'orange')
        self.center_block = self.blocks[1]


class L_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x, center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'cyan')
        self.center_block = self.blocks[1]


class O_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x, center.y),
                  Point(center.x - 1, center.y),
                  Point(center.x, center.y + 1),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'red')
        self.center_block = self.blocks[0]

    def rotate(self, board):
        # Override Shape's rotate method since O_Shape does not rotate
        return


class S_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x, center.y),
                  Point(center.x, center.y + 1),
                  Point(center.x + 1, center.y),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'green')
        self.center_block = self.blocks[0]
        self.shift_rotation_dir = True
        self.rotation_dir = -1


class T_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x, center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x, center.y + 1)]
        Shape.__init__(self, coords, 'yellow')
        self.center_block = self.blocks[1]


class Z_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x, center.y),
                  Point(center.x, center.y + 1),
                  Point(center.x + 1, center.y + 1)]
        Shape.__init__(self, coords, 'magenta')
        self.center_block = self.blocks[1]
        self.shift_rotation_dir = True
        self.rotation_dir = -1

    ############################################################


# BOARD CLASS
############################################################


class Board(object):
    ''' Board class: it represents the Tetris board

        Attributes: width - type:int - width of the board in squares
                    height - type:int - height of the board in squares
                    canvas - type:CanvasFrame - where the pieces will be drawn
                    grid - type:Dictionary - keeps track of the current state of
                    the board; stores the blocks for a given position
    '''

    def __init__(self, win, width, height):
        self.width = width
        self.height = height

        # create a canvas to draw the tetris shapes on
        self.canvas = CanvasFrame(win, self.width * Block.BLOCK_SIZE,
                                  self.height * Block.BLOCK_SIZE)
        self.canvas.setBackground('light gray')

        # create an empty dictionary
        # currently we have no shapes on the board
        self.grid = {}

        self.DEBUG_X = -1
        self.DEBUG_Y = -1

    def draw_shape(self, shape):
        ''' Parameters: shape - type: Shape
            Return value: type: bool

            draws the shape on the board if there is space for it
            and returns True, otherwise it returns False
        '''

        if self.DEBUG_X != -1 and self.DEBUG_Y != -1:
            self.grid[self.DEBUG_X, self.DEBUG_Y] = shape.get_blocks()[0]
            # TODO: row(board, y) != []
        if shape.can_move(self, 0, 0):
            shape.draw(self.canvas)
            return True
        return False

    def can_move(self, x, y):
        ''' Parameters: x - type:int
                        y - type:int
            Return value: type: bool

            1. check if it is ok to move to square x,y
            if the position is outside of the board boundaries, can't move there
            return False

            2. if there is already a block at that position, can't move there
            return False

            3. otherwise return True

        '''

        # Check that (x, y) is within the boundaries of the board.
        if (x < 0 or x >= self.width) or (y < 0 or y >= self.height):
            return False

        # Check that there is no block at that location.
        return (x, y) not in self.grid

    def add_shape(self, shape):
        ''' Parameter: shape - type:Shape

            add a shape to the grid, i.e.
            add each block to the grid using its
            (x, y) coordinates as a dictionary key

            Hint: use the get_blocks method on Shape to
            get the list of blocks

        '''
        blocks = shape.get_blocks()
        for block in blocks:
            self.grid[(block.x, block.y)] = block

    def row(self, y):
        # TODO: Implement.
        # return filter(lambda block: block[1] == y, self.grid)
        extracted_row = []
        for block in self.grid:
            if block[1] == y:
                extracted_row.append(block)

        return extracted_row

    @PaladinPostCondition("never exists row(board, y)")
    def delete_row(self, y):
        """
            Parameters: y - type:int

            remove all the blocks in row y
            to remove a block you must remove it from the grid
            and erase it from the screen.
            If you don\'t remember how to erase a graphics object
            from the screen, take a look at the Graphics Library
            handout

        """

        # Remove the blocks in the row from the grid.
        grid_blocks_keys = self.grid.copy().keys()
        for _x, _y in filter(lambda k: k[1] == y, grid_blocks_keys):
            # Undraw from screen.
            self.grid[_x, _y].undraw()

            # Remove from grid.
            del self.grid[_x, _y]

            self.DEBUG_X = _x
            self.DEBUG_Y = _y

    def is_row_complete(self, y):
        ''' Parameter: y - type: int
            Return value: type: bool

            for each block in row y
            check if there is a block in the grid (use the in operator)
            if there is one square that is not occupied, return False
            otherwise return True

        '''
        r = range(0, self.width)
        return all((x, y) in self.grid for x in r)

    def move_down_rows(self, y_start):
        ''' Parameters: y_start - type:int

            for each row from y_start to the top
                for each column
                    check if there is a block in the grid
                    if there is, remove it from the grid
                    and move the block object down on the screen
                    and then place it back in the grid in the new position

        '''
        r = range(0, y_start)
        for k in r:
            y = y_start - k
            for x in [_x for (_x, _y) in self.grid if _y == y]:
                # Remove it from the grid.
                block = self.grid.pop((x, y))
                block.move(0, 1)
                # Replace it in the grid.
                # self.grid[(x, y + 1)] = block

    def remove_complete_rows(self):
        """ removes all the complete rows
            1. for each row, y,
            2. check if the row is complete
                if it is,
                    delete the row
                    move all rows down starting at row y - 1

        """
        r = 1
        while r < self.height:
            y = self.height - r
            if self.is_row_complete(y):
                # Delete the row.
                self.delete_row(y)

                # Push down all the rows beneath
                self.move_down_rows(y - 1)
                r -= 1
            r += 1

    def game_over(self):
        ''' display "Game Over !!!" message in the center of the board
            HINT: use the Text class from the graphics library
        '''
        w = int(self.width / 2)
        h = int(self.height / 2)
        p = Point(w, h)
        text = Text(p, "Game Over !!!")
        text.draw(self.canvas)
        win.destroy()

    def __str__(self):
        return f"Board({id(self)}): {[(x, y) for x, y in self.grid]}"


############################################################


# TETRIS CLASS
############################################################

class Tetris(object):
    ''' Tetris class: Controls the game play
        Attributes:
            SHAPES - type: list (list of Shape classes)
            DIRECTION - type: dictionary - converts string direction to (dx, dy)
            BOARD_WIDTH - type:int - the width of the board
            BOARD_HEIGHT - type:int - the height of the board
            board - type:Board - the tetris board
            win - type:Window - the window for the tetris game
            delay - type:int - the speed in milliseconds for moving the shapes
            current_shapes - type: Shape - the current moving shape on the board
    '''

    SHAPES = [I_shape, J_shape, L_shape, O_shape, S_shape, T_shape, Z_shape]
    DIRECTION = {'Left': (-1, 0), 'Right': (1, 0), 'Down': (0, 1)}
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    __TEST_MODE = True

    def __init__(self, win):
        self.board = Board(win, self.BOARD_WIDTH, self.BOARD_HEIGHT)
        self.win = win
        self.delay = 500  # ms

        self.TEST_MOCK_COUNTER_X = -1
        self.TEST_MOCK_COUNTER_Y = self.BOARD_HEIGHT - 2

        # sets up the keyboard events
        # when a key is called the method key_pressed will be called
        self.win.bind_all('<Key>', self.key_pressed)

        # set the current shape to a random new shape
        self.current_shape = self.create_new_shape()

        # Draw the current_shape on the board (take a look at the
        # draw_shape method in the Board class)
        self.board.draw_shape(self.current_shape)

        # For Step 9:  animate the shape!
        self.animate_shape()

    def create_new_shape(self):
        ''' Return value: type: Shape

            Create a random new shape that is centered
             at y = 0 and x = int(self.BOARD_WIDTH/2)
            return the shape
        '''

        # shape_class = random.choice(Shape.__subclasses__())
        # return shape_class(Point(x=int(self.BOARD_WIDTH / 2), y=0))
        return O_shape(Point(self.BOARD_WIDTH / 2, y=0))

    def animate_shape(self):
        ''' animate the shape - move down at equal intervals
            specified by the delay attribute
        '''

        next_move = self.do_move('Down')
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
        # Extract the differences in the grid by the direction.
        dx, dy = self.DIRECTION[direction]

        # Check if the current shape can move.
        if self.current_shape.can_move(self.board, dx, dy):
            # Move it.
            self.current_shape.move(dx, dy)
            # Leave.
            return True

        # Otherwise, If direction is not 'Down', leave.
        if direction != 'Down':
            return False

        # The direction is Down, add the new shape to the board.
        self.board.add_shape(self.current_shape)

        # Remove complete rows.
        self.board.remove_complete_rows()

        # Randomize a new shape and set it as the current one.
        self.current_shape = self.create_new_shape()

        # Check if the shape can be added to the board.
        if not self.board.draw_shape(self.current_shape):
            # Notify that the game is over and leave.
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
        ''' this function is called when a key is pressed on the keyboard
            it currenly just prints the value of the key

            Modify the function so that if the user presses the arrow keys
            'Left', 'Right' or 'Down', the current_shape will move in
            the appropriate direction

            if the user presses the space bar 'space', the shape will move
            down until it can no longer move and is added to the board

            if the user presses the 'Up' arrow key ,
                the shape should rotate.

        '''
        key = event.keysym

        if key in self.DIRECTION:
            self.do_move(key)

        elif key == 'space':
            shape_going_down = self.current_shape
            while self.do_move('Down'):
                if shape_going_down is not self.current_shape:
                    break

        elif key == 'Up':
            self.do_rotate()

        # TODO: THIS IS FOR TESTING!!!
        if key == 'Q' or key == 'q':
            self.board.game_over()


################################################################
# Start the game
################################################################
if __name__ == '__main__':
    Paladin.resume_record()
    win = Window("Tetris")
    game = Tetris(win)
    win.mainloop()
