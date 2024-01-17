import pygame
import random
import numpy as np
import tcod

pygame.init()
LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3,
NONE = 4
running = True
WIDTH = 800
HEIGHT = 800
GHOSTS = []
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Заставка для игры")
background = pygame.image.load("data/fon.jpg")
font_name = pygame.font.match_font('arial', 30)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            running = False
        if event.type == pygame.QUIT:
            running = False
    screen.blit(background, (0, 0))
    draw_text(screen, f'Правила игры:', 50, 350, 0)
    draw_text(screen, f'Передвижение по стрелочкам', 50, 350, 100)
    draw_text(screen, f'Старайтесь не попасться призракам', 50, 350, 200)
    draw_text(screen, f'Ешьте печенье', 50, 350, 300)
    pygame.display.flip()


def trans_2(coords):
    return int(coords[0] / 32), int(coords[1] / 32)


def trans_1(coords):
    return coords[0] * 32, coords[1] * 32


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.rstrip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


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
        return pygame.Rect(self.x, self.y, self.size, self.size)

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
        self.cookies = []
        self.lives = 3

    def tick(self, fps: int):
        while not self.ready:
            for object in self.objects:
                object.tick()
                object.draw()
            draw_text(self.screen, f'ЖИЗНЕЙ {str(self.lives)} ОЧКОВ {str(self.hero.score)}', 18, 100, 0)
            pygame.display.flip()
            self.clock.tick(fps)
            self.screen.fill((0, 0, 0))
            self.events_helper()
        print("Game over")

    def add_object(self, obj: Object):
        self.objects.append(obj)

    def add_wall(self, obj: Wall):
        self.add_object(obj)
        self.walls.append(obj)

    def get_cookies(self):
        return self.cookies

    def get_walls(self):
        return self.walls

    def quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ready = True

    def add_hero(self, hero):
        self.add_object(hero)
        self.hero = hero

    def events_helper(self):
        collision = pygame.Rect(self.hero.get_pos()[0], self.hero.get_pos()[1], self.hero.size, self.hero.size)
        collision1 = pygame.Rect(ghost1.get_pos()[0], ghost1.get_pos()[1], ghost1.size, ghost1.size)
        collides1 = collision.colliderect(collision1)
        if ghost2:
            collision2 = pygame.Rect(ghost2.get_pos()[0], ghost2.get_pos()[1], ghost2.size, ghost2.size)
            collides2 = collision.colliderect(collision2)
        else:
            collides2 = False
        if ghost3:
            collision3 = pygame.Rect(ghost3.get_pos()[0], ghost3.get_pos()[1], ghost3.size, ghost3.size)
            collides3 = collision.colliderect(collision3)
        else:
            collides3 = False
        if ghost4:
            collision4 = pygame.Rect(ghost4.get_pos()[0], ghost4.get_pos()[1], ghost4.size, ghost4.size)
            collides4 = collision.colliderect(collision4)
        else:
            collides4 = False
        if collides1 or collides2 or collides3 or collides4:
            self.kill_pacman()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ready = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.hero.set_dir(UP)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.hero.set_dir(LEFT)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.hero.set_dir(DOWN)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.hero.set_dir(RIGHT)

    def get_game_objects(self):
        return self.objects

    def add_cookie(self, obj: Object):
        self.objects.append(obj)
        self.cookies.append(obj)

    def kill_pacman(self):
        self.lives -= 1
        self.hero.set_pos(32, 32)
        self.hero.set_dir(NONE)
        if self.lives == 0:
            self.end_game()

    def end_game(self):
        self.ready = True
        running = True
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Заставка для игры")
        background = pygame.image.load("data/fon.jpg")


        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                if event.type == pygame.QUIT:
                    running = False
            screen.blit(background, (0, 0))
            draw_text(screen, f'Вы проиграли', 50, 350, 0)
            draw_text(screen, f'Ваши очки: {self.hero.score}', 50, 350, 100)
            pygame.display.flip()


class MovableObject(Object):
    def __init__(self, surface, x, y, size: int, color=(255, 0, 0), circle: bool = False):
        super().__init__(surface, x, y, size, color, circle)
        self.cur_dir = NONE
        self.dir_buffer = NONE
        self.image = pygame.image.load('data/ghost.png')
        self.last_dir = NONE
        self.porydok = []
        self.next_target = None
        self.x = x
        self.y = y

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

    def check_reachable(self, direction: int):
        des_position = (0, 0)
        if direction == NONE:
            return False, des_position
        if direction == UP:
            des_position = (self.x, self.y - 1)
        elif direction == DOWN:
            des_position = (self.x, self.y + 1)
        elif direction == LEFT:
            des_position = (self.x - 1, self.y)
        elif direction == RIGHT:
            des_position = (self.x + 1, self.y)

        return self.bit_wall(des_position), des_position

    def automatic_move(self, direction):
        pass

    def tick(self):
        self.ready_aim()
        self.automatic_move(self.cur_dir)

    def ready_aim(self):
        pass

    def draw(self):
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.surface.blit(self.image, self.get_shape())


class Ghost(MovableObject):
    def __init__(self, surface, x, y, size: int, controller, sprite_path="data/ghost_ghost.png", color=(255, 0, 0)):
        super().__init__(surface, x, y, size, color, False)
        self.controller = controller
        self.sprite_normal = pygame.image.load(sprite_path)

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

    def draw(self):
        self.image = self.sprite_normal
        super(Ghost, self).draw()


class Pathfinder:
    def __init__(self, arr):
        cost = np.array(arr, dtype=np.bool_).tolist()
        self.pf = tcod.path.AStar(cost=cost, diagonal=0)

    def get_path(self, from_x, from_y, to_x, to_y):
        res = self.pf.get_path(from_x, from_y, to_x, to_y)
        return [(sub[1], sub[0]) for sub in res]


class Controller:
    def __init__(self):
        self.ascii_maze = load_level('map1.txt')

        self.maze = []
        self.point_spaces = []
        self.reachable_spaces = []
        self.ghost_spawns = []
        self.cookie_spaces = []

        self.size = (0, 0)
        self.convert()
        self.ghost_colors = [
            "data/ghost.png",
            "data/ghost_pink.png",
            "data/ghost_orange.png",
            "data/ghost_blue.png"
        ]
        self.p = Pathfinder(self.maze)

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
                    self.cookie_spaces.append((y, x))
                    self.reachable_spaces.append((y, x))
            self.maze.append(binary_row)


class Hero(MovableObject):
    def __init__(self, surface, x, y, size: int):
        super().__init__(surface, x, y, size, (255, 255, 0), False)
        self.last_position = (0, 0)
        self.score = 0
        self.image = pygame.image.load("data/paku.png")

    def tick(self):
        if self.x < 0:
            self.x = self.rend.width

        if self.x > self.rend.width:
            self.x = 0

        self.last_position = self.get_pos()

        if self.check_reachable(self.dir_buffer)[0]:
            self.automatic_move(self.cur_dir)
        else:
            self.automatic_move(self.dir_buffer)
            self.cur_dir = self.dir_buffer

        if self.bit_wall((self.x, self.y)):
            self.set_pos(self.last_position[0], self.last_position[1])

        self.cookie_pickup()

    def automatic_move(self, in_direction: int):
        if_collides = self.check_reachable(in_direction)

        next_pos = if_collides[0]
        if not next_pos:
            self.last_dir = self.cur_dir
            desired_position = if_collides[1]
            self.set_pos(desired_position[0], desired_position[1])
        else:
            self.cur_dir = self.last_dir

    def cookie_pickup(self):
        collision_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        cookies = self.rend.get_cookies()
        game_objects = self.rend.get_game_objects()
        for cookie in cookies:
            collides = collision_rect.colliderect(cookie.get_shape())
            if collides and cookie in game_objects:
                game_objects.remove(cookie)
                self.score += 1

    def draw(self):
        super(Hero, self).draw()


class Cookie(Object):
    def __init__(self, surface, x, y):
        super().__init__(surface, x, y, 4, (255, 255, 0), True)


if __name__ == "__main__":
    unified_size = 32
    pacman_game = Controller()
    size = pacman_game.size
    game_renderer = Renderer(size[0] * unified_size, size[1] * unified_size)
    for y, row in enumerate(pacman_game.maze):
        for x, column in enumerate(row):
            if column == 0:
                game_renderer.add_wall(Wall(game_renderer, x, y, unified_size))

    for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
        translated = trans_1(ghost_spawn)
        ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                      pacman_game.ghost_colors[i % 4])
        game_renderer.add_object(ghost)
        GHOSTS.append(ghost)
    if len(GHOSTS) == 4:
        ghost1 = GHOSTS[0]
        ghost2 = GHOSTS[1]
        ghost3 = GHOSTS[2]
        ghost4 = GHOSTS[3]
    elif len(GHOSTS) == 3:
        ghost1 = GHOSTS[0]
        ghost2 = GHOSTS[1]
        ghost3 = GHOSTS[2]
        ghost4 = None
    elif len(GHOSTS) == 2:
        ghost1 = GHOSTS[0]
        ghost2 = GHOSTS[1]
        ghost3 = None
        ghost4 = None
    elif len(GHOSTS) == 1:
        ghost1 = GHOSTS[0]
        ghost2 = None
        ghost3 = None
        ghost4 = None
    for cookie_space in pacman_game.cookie_spaces:
        translated = trans_1(cookie_space)
        cookie = Cookie(game_renderer, translated[0] + unified_size / 2, translated[1] + unified_size / 2)
        game_renderer.add_cookie(cookie)
    pacman = Hero(game_renderer, unified_size, unified_size, unified_size)
    game_renderer.add_hero(pacman)
    game_renderer.tick(120)
