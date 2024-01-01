import pygame


class Direction():
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3,
    NONE = 4


def translate_screen_to_maze(coords, size=32):
    return int(coords[0] / size), int(coords[1] / size)


def translate_maze_to_screen(coords, size=32):
    return coords[0] * size, coords[1] * size


class Object:
    def __init__(self, surface, x, y,
                 size: int, color=(255, 0, 0),
                 circle: bool = False):
        self.size = size
        self.renderer = surface
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
            rect_object = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(self.surface,
                             self.color,
                             rect_object,
                             border_radius=4)

    def tick(self):
        pass

    def get_shape(self):
        return self.shape

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
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
        self.done = False
        self.game_objects = []
        self.walls = []
        self.points = []

    def tick(self, fps: int):
        black = (0, 0, 0)
        while not self.done:
            for game_object in self.game_objects:
                game_object.tick()
                game_object.draw()

            pygame.display.flip()
            self.clock.tick(fps)
            self.screen.fill(black)
            self.handle_events()
        print("Game over")

    def add_game_object(self, obj: Object):
        self.game_objects.append(obj)

    def add_wall(self, obj: Wall):
        self.add_game_object(obj)
        self.walls.append(obj)

    def get_walls(self):
        return self.walls

    def quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

    def add_hero(self, hero):
        self.add_game_object(hero)
        self.hero = hero

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.hero.set_direction(Direction.UP)
        elif pressed[pygame.K_LEFT]:
            self.hero.set_direction(Direction.LEFT)
        elif pressed[pygame.K_DOWN]:
            self.hero.set_direction(Direction.DOWN)
        elif pressed[pygame.K_RIGHT]:
            self.hero.set_direction(Direction.RIGHT)

    def get_game_objects(self):
        return self.game_objects


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


class MovableObject(Object):
    def __init__(self, surface, x, y, size: int, color=(255, 0, 0), circle: bool = False):
        super().__init__(surface, x, y, size, color, circle)
        self.cur_dir = Direction.NONE
        self.dir_buffer = Direction.NONE
        self.last_dir = Direction.NONE
        self.queue = []
        self.next_target = None

    def get_next_location(self):
        if len(self.queue) == 0:
            return None
        else:
            self.queue.pop(0)

    def set_direction(self, direction):
        self.cur_dir = direction
        self.dir_buffer = direction

    def collides_with_wall(self, position):
        collision_rect = pygame.Rect(position[0], position[1], self.size, self.size)
        collides = False
        walls = self.renderer.get_walls()
        for wall in walls:
            collides = collision_rect.colliderect(wall.get_shape())
            if collides:
                break
        return collides

    def check_collision_in_direction(self, direction: Direction):
        des_position = (0, 0)
        if direction == Direction.NONE:
            return False, des_position
        if direction == Direction.UP:
            des_position = (self.x, self.y - 1)
        elif direction == Direction.DOWN:
            des_position = (self.x, self.y + 1)
        elif direction == Direction.LEFT:
            des_position = (self.x - 1, self.y)
        elif direction == Direction.RIGHT:
            des_position = (self.x + 1, self.y)

        return self.collides_with_wall(des_position), des_position


class Ghost(MovableObject):
    def __init__(self, surface, x, y, size: int, game_controller, color=(255, 0, 0)):
        super().__init__(surface, x, y, size, color, False)
        self.game_controller = game_controller


class Hero(MovableObject):
    def __init__(self, in_surface, x, y, in_size: int):
        super().__init__(in_surface, x, y, in_size, (255, 255, 0), False)
        self.last_non_colliding_position = (0, 0)

    def tick(self):
        if self.x < 0:
            self.x = self.renderer.width

        if self.x > self.renderer.width:
            self.x = 0

        self.last_non_colliding_position = self.get_position()

        if self.check_collision_in_direction(self.dir_buffer)[0]:
            self.automatic_move(self.cur_dir)
        else:
            self.automatic_move(self.dir_buffer)
            self.current_direction = self.dir_buffer

        if self.collides_with_wall((self.x, self.y)):
            self.set_position(self.last_non_colliding_position[0], self.last_non_colliding_position[1])

    def automatic_move(self, in_direction: Direction):
        collision_result = self.check_collision_in_direction(in_direction)

        desired_position_collides = collision_result[0]
        if not desired_position_collides:
            self.last_working_direction = self.cur_dir
            desired_position = collision_result[1]
            self.set_position(desired_position[0], desired_position[1])
        else:
            self.cur_dir = self.last_working_direction

    def draw(self):
        half_size = self.size / 2
        pygame.draw.circle(self.surface, self.color, (self.x + half_size, self.y + half_size), half_size)


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
        translated = translate_maze_to_screen(ghost_spawn)
        ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                      pacman_game.ghost_colors[i % 4])
        game_renderer.add_game_object(ghost)

    pacman = Hero(game_renderer, unified_size, unified_size, unified_size)
    game_renderer.add_hero(pacman)
    game_renderer.tick(120)
