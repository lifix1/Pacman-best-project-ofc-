import pygame
import random
import tcod
import numpy as np



LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3,
NONE = 4


def trans_2(coords):
    return int(coords[0] / 32), int(coords[1] / 32)


def trans_1(coords):
    return coords[0] * 32, coords[1] * 32


class Object:
    def __init__(self, surface, x, y,
                 size: int, color=(255, 0, 0),
                 circle: bool = False):
        self.size = size
        self.rend = surface
        self.surface = surface.screen
        self.y = y
        self.x = x
        self.color = color
        self.circle = circle
        self.shape = pygame.Rect(self.x, self.y, size, size)

    def draw(self):
        if self.circle:
            pygame.draw.circle(self.surface,
                               self.color,
                               (self.x, self.y),
                               self.size)
        else:
            object = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(self.surface,
                             self.color,
                             object,
                             border_radius=4)

    def tick(self):
        pass

    def get_shape(self):
        return self.shape

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y


class Wall(Object):
    def __init__(self, surface, x, y, size: int, color=(0, 0, 255)):
        super().__init__(surface, x * size, y * size, size, color)


class Renderer:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Pacman')
        self.clock = pygame.time.Clock()
        self.ready = False
        self.objects = []
        self.walls = []
        self.points = []

    def tick(self, fps: int):
        black = (0, 0, 0)
        while not self.ready:
            for object in self.objects:
                object.tick()
                object.draw()

            pygame.display.flip()
            self.clock.tick(fps)
            self.screen.fill(black)
            self.quit()
        print("Game over")

    def add_object(self, obj: Object):
        self.objects.append(obj)

    def add_wall(self, obj: Wall):
        self.add_object(obj)
        self.walls.append(obj)

    def quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ready = True


class MovableObject(Object):
    def __init__(self, surface, x, y, size: int, color=(255, 0, 0), circle: bool = False):
        super().__init__(surface, x, y, size, color, circle)
        self.cur_dir = NONE
        self.dir_buffer = NONE
        self.last_dir = NONE
        self.porydok = []
        self.next_target = None

    def next_coord(self):
        return None if len(self.porydok) == 0 else self.porydok.pop(0)

    def set_dir(self, direction):
        self.cur_dir = direction
        self.dir_buffer = direction

    def bit_wall(self, pos):
        collision = pygame.Rect(pos[0], pos[1], self.size, self.size)
        collides = False
        walls = self.rend.get_walls()
        for wall in walls:
            collides = collision.colliderect(wall.get_shape())
            if collides:
                break
        return collides

    def check_bit_direction(self, direction):
        des_pos = (0, 0)
        if direction == NONE:
            return False, des_pos
        if direction == UP:
            des_pos = (self.x, self.y - 1)
        elif direction == DOWN:
            des_pos = (self.x, self.y + 1)
        elif direction == LEFT:
            des_pos = (self.x - 1, self.y)
        elif direction == RIGHT:
            des_pos = (self.x + 1, self.y)

        return self.bit_wall(des_pos), des_pos

    def automatic_move(self, direction):
        pass

    def tick(self):
        self.ready_aim()
        self.automatic_move(self.cur_dir)

    def ready_aim(self):
        pass


class Ghost(MovableObject):
    def __init__(self, surface, x, y, size: int, controller, color=(255, 0, 0)):
        super().__init__(surface, x, y, size, color, False)
        self.controller = controller

    def ready_aim(self):
        if (self.x, self.y) == self.next_target:
            self.next_target = self.next_coord()
        self.cur_dir = self.calc_dir_next_target()

    def set_new_path(self, path):
        for item in path:
            self.porydok.append(item)
        self.next_target = self.next_coord()

    def calc_dir_next_target(self):
        if self.next_target is None:
            self.controller.make_new_way(self)
            return NONE
        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return DOWN if diff_y > 0 else UP
        if diff_y == 0:
            return LEFT if diff_x < 0 else RIGHT
        self.controller.make_new_way(self)
        return NONE

    def automatic_move(self, direction):
        if direction == UP:
            self.set_pos(self.x, self.y - 1)
        elif direction == DOWN:
            self.set_pos(self.x, self.y + 1)
        elif direction == LEFT:
            self.set_pos(self.x - 1, self.y)
        elif direction == RIGHT:
            self.set_pos(self.x + 1, self.y)


class Pathfinder:
    def __init__(self, arr):
        cost = np.array(arr, dtype=np.bool_).tolist()
        self.pf = tcod.path.AStar(cost=cost, diagonal=0)

    def get_path(self, from_x, from_y, to_x, to_y):
        res = self.pf.get_path(from_x, from_y, to_x, to_y)
        return [(sub[1], sub[0]) for sub in res]


class Controller:
    def __init__(self):
        self.ascii_maze = [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP           XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X                          X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X      XX    XX    XX      X",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX X   G  X XX XXXXXX",
            "          X G    X          ",
            "XXXXXX XX X   G  X XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "X            XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X   XX       G        XX   X",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "X      XX    XX    XX      X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X                          X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.numpy_maze = []
        self.point_spaces = []
        self.reachable_spaces = []
        self.ghost_spawns = []

        self.size = (0, 0)
        self.convert()
        self.ghost_colors = [
            (255, 184, 255),
            (255, 0, 20),
            (0, 255, 255),
            (255, 184, 82)
        ]
        self.p = Pathfinder(self.numpy_maze)

    def make_new_way(self, ghost: Ghost):
        random_space = random.choice(self.reachable_spaces)
        current_maze_coord = trans_2(ghost.get_pos())

        path = self.p.get_path(current_maze_coord[1], current_maze_coord[0], random_space[1],
                               random_space[0])
        test_path = [trans_1(item) for item in path]
        ghost.set_new_path(test_path)

    def convert(self):
        for x, row in enumerate(self.ascii_maze):
            self.size = (len(row), x + 1)
            binary_row = []
            for y, column in enumerate(row):
                if column == "G":
                    self.ghost_spawns.append((y, x))

                if column == "X":
                    binary_row.append(0)
                else:
                    binary_row.append(1)
                    self.point_spaces.append((y, x))
                    self.reachable_spaces.append((y, x))
            self.numpy_maze.append(binary_row)


if __name__ == "__main__":
    unified_size = 32
    pacman_game = Controller()
    size = pacman_game.size
    game_renderer = Renderer(size[0] * unified_size, size[1] * unified_size)

    for y, row in enumerate(pacman_game.numpy_maze):
        for x, column in enumerate(row):
            if column == 0:
                game_renderer.add_wall(Wall(game_renderer, x, y, unified_size))

    for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
        translated = trans_1(ghost_spawn)
        ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                      pacman_game.ghost_colors[i % 4])
        game_renderer.add_object(ghost)

    game_renderer.tick(120)
