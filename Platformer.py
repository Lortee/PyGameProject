import pygame
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

pygame.display.set_caption("Platformer")

font_score = pygame.font.Font('Pixel.ttf', 23)

tile_size = 40
game_over = 0
main_menu = True
score = 0
level = 1
c = 0
sound = True
clicked = False

# IMAGES
bg1_img = pygame.image.load("res/images/background_layer_1.1.png")
bg2_img = pygame.image.load("res/images/background_layer_2.2.png")
bg3_img = pygame.image.load("res/images/background_layer_3.3.png")
restart_img = pygame.image.load("res/images/Restart.png")
start_img = pygame.image.load("res/images/Menu.png")
exit_img_main = pygame.image.load("res/images/Exit_main.png")
exit_img = pygame.image.load("res/images/Exit.png")
exit_img_main = pygame.transform.scale(exit_img_main, (288, 110))
continue_img = pygame.image.load("res/images/Continue.png")
coin_dark = pygame.image.load("res/images/Not_coin.png")
coin_dark = pygame.transform.scale(coin_dark, (100, 100))
coin_img = pygame.image.load("res/images/Coin.png")
coin_img = pygame.transform.scale(coin_img, (100, 100))
coin_main_img = pygame.transform.scale(coin_img, (40, 40))
coin_main_dark = pygame.transform.scale(coin_dark, (40, 40))

mini_coin_img = pygame.transform.scale(coin_img, (20, 20))
first_img = pygame.image.load("res/images/first_level.png")
first_img = pygame.transform.scale(first_img, (110, 110))
second_img = pygame.image.load("res/images/second_img.png")
second_img = pygame.transform.scale(second_img, (110, 110))

soundon_img = pygame.image.load("res/images/sound_on.png")
soundon_img = pygame.transform.scale(soundon_img, (55, 55))
soundoff_img = pygame.image.load("res/images/sound_off.png")
soundoff_img = pygame.transform.scale(soundoff_img, (55, 55))

color_brown = (115, 66, 34)
color_brown_dark = (77, 34, 14)
color_white = (255, 255, 255)
color_black = (0, 0, 0)

coin_fx = pygame.mixer.Sound("res/sounds/coin_sound.mp3")
coin_fx.set_volume(0.5)
# back_fx = pygame.mixer.Sound("res/sounds/backmusic.mp3")
# back_fx.set_volume(0.01)
mixer.music.load("res/sounds/backmusic.mp3")
mixer.music.set_volume(0.01)
mixer.music.play()
game_over_fx = pygame.mixer.Sound("res/sounds/die.mp3")
game_over_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound("res/sounds/jump.mp3")
jump_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(lvl):
    global worlds, coordinate
    if lvl == 1:
        coordinate = (50, screen_height - 120)
    if lvl == 2:
        coordinate = (50, 50)

    player.reset(*coordinate)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    if lvl == 1:
        worlds = World(world_data_level_1)
    if lvl == 2:
        worlds = World(world_data_level_2)

    return worlds


def draw_grid():
    for line in range(0, 18):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.in_air = False
        self.vel_y = 0
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.jumped = False
        self.reset(x, y)

    def update(self, game_over):
        global w
        dx = 0
        dy = 0
        # СКОРОСТЬ АНИМАЦИИ
        walk_cooldown = 5

        if game_over == 0:

            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped is False and self.in_air is False:
                if sound:
                    jump_fx.play()
                # back_fx.play()
                self.vel_y = -14
                self.jumped = True
            if key[pygame.K_UP] is False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] is False and key[pygame.K_RIGHT] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.in_air = True

            if level == 1:
                w = world
            elif level == 2:
                w = world
            for tile in w.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, blob_group, False):
                if sound:
                    game_over_fx.play()
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                if sound:
                    game_over_fx.play()
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
            if self.rect.right > screen_width:
                self.rect.right = screen_width
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.left <= 0:
                self.rect.left = 0

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y <= 720:
                self.rect.y += 5

        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 6):
            img_right = pygame.image.load(f"res/images/right{num}.png")
            img_right = pygame.transform.scale(img_right, (30, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        i = pygame.image.load("res/images/dead.png")
        self.dead_image = pygame.transform.scale(i, (60, 30))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World:
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load("res/images/dirt_up.png")
        dirt2_img = pygame.image.load("res/images/dirt_down.png")
        dirt3_img = pygame.image.load("res/images/dirt_left.png")
        dirt4_img = pygame.image.load("res/images/dirt_right.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(dirt2_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(dirt3_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = pygame.transform.scale(dirt4_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 16)
                    blob_group.add(blob)
                if tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + 16)
                    coin_group.add(coin)
                if tile == 7:
                    # img = pygame.transform.scale(lava2_img, (tile_size, tile_size))
                    # img_rect = img.get_rect()
                    # img_rect.x = col_count * tile_size
                    # img_rect.y = row_count * tile_size
                    # tile = (img, img_rect)
                    # self.tile_list.append(tile)
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_rigth = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img_right = pygame.image.load(f"res/images/slime{num}.png")
            img_right = pygame.transform.scale(img_right, (30, 25))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_rigth.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_rigth[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        walk_cooldown = 15
        self.rect.x += self.move_direction
        self.move_counter += 1
        self.counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1

            self.move_counter *= -1
            self.counter *= -1
        if self.move_direction == -1:
            self.image = self.images_rigth[self.index]
        else:
            self.image = self.images_left[self.index]

        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_rigth):
                self.index = 0
            if self.move_direction == -1:
                self.image = self.images_rigth[self.index]
            else:
                self.image = self.images_left[self.index]


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("res/images/lava2.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("res/images/Coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("res/images/Door.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# class Continue(pygame.sprite.Sprite):
#     def __init__(self, x, y):
#         pygame.sprite.Sprite.__init__(self)
#
#         img = pygame.image.load("res/images/Continue.png")
#         self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
#         self.rect = self.image.get_rect()
#         self.rect.x = x
#         self.rect.y = y


run = True

while run:
    # back_fx.play(-1)

    if c == 0:
        world_data_level_1 = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 8],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 3, 1, 4],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 3, 1, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 5, 0, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 1, 4, 7, 7, 7, 7, 7, 7, 3, 1, 1, 1],
            [0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        ]
        world_data_level_2 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 4, 0, 0, 0, 3, 4, 0, 0, 0, 0, 3, 4, 0, 0, 0],
            [0, 0, 0, 1, 4, 7, 7, 3, 1, 4, 7, 7, 3, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 4],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 5, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 2, 2, 2, 2],
            [0, 0, 0, 5, 0, 0, 5, 0, 0, 3, 1, 1, 1, 2, 2, 2, 2, 2],
            [0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [7, 3, 1, 4, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 4, 7, 7, 7, 7, 7, 3, 1, 4, 0, 0, 0, 0, 0],
            [2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 0, 0, 8],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
        ]
        if level == 1:
            coordinates = (50, screen_height - 120)
        if level == 2:
            coordinates = (50, 50)
        player = Player(*coordinates)

        blob_group = pygame.sprite.Group()
        lava_group = pygame.sprite.Group()
        exit_group = pygame.sprite.Group()
        coin_group = pygame.sprite.Group()

        if level == 1:
            world = World(world_data_level_1)
        if level == 2:
            world = World(world_data_level_2)

        restart_button = Button(101 + 94, 5, restart_img)
        start_button = Button(5, 5, start_img)
        exit_button = Button(96, 5, exit_img)
        first_button = Button(screen_width // 2 - 288 // 2, screen_height // 2 - 130, first_img)
        second_button = Button(screen_width // 2 + 35, screen_height // 2 - 130, second_img)
        exit_button_main = Button(screen_width // 2 - 288 // 2, screen_height // 2 + 30, exit_img_main)

    if sound:
        sound_button = Button(screen_width - 55 - 5, 5, soundoff_img)

    else:
        sound_button = Button(screen_width - 55 - 5, 5, soundon_img)
    c = 1

    clock.tick(fps)

    screen.blit(bg1_img, (0, 0))
    screen.blit(bg2_img, (0, 0))
    screen.blit(bg3_img, (0, 0))

    if main_menu is True:
        score = 0
        if exit_button_main.draw():
            run = False
        if sound_button.draw() and clicked is False:
            sound = not sound
            if sound:
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.stop()
            clicked = True
        if first_button.draw():
            level = 1
            main_menu = False
            c = 0
        if second_button.draw():
            level = 2
            main_menu = False
            c = 0
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                clicked = False

        f = open("res/levels.txt", "r")
        a = str(f.read())
        l1 = int(a[0])
        l2 = int(a[2])

        if l1 == 0:
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 - 5, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35, screen_height // 2 - 50))
        if l1 == 1:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35, screen_height // 2 - 50))
        if l1 == 2:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35, screen_height // 2 - 50))
        if l1 == 3:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35 + 5 + 35, screen_height // 2 - 50))

        if l2 == 0:
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 - 5 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35 + 178, screen_height // 2 - 50))
        if l2 == 1:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35 + 178, screen_height // 2 - 50))
        if l2 == 2:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35 + 178, screen_height // 2 - 50))
            screen.blit(coin_main_dark, (screen_width // 2 - 288 // 2 + 35 + 5 + 35 + 178, screen_height // 2 - 50))
        if l2 == 3:
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 - 5, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35, screen_height // 2 - 50))
            screen.blit(coin_main_img, (screen_width // 2 - 288 // 2 + 35 + 5 + 35, screen_height // 2 - 50))
    else:
        # if level == 1:
        #     world.draw()
        # elif level == 2:
        world.draw()
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = True
            game_over = 0

        if game_over == 0:
            blob_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                if sound:
                    coin_fx.play()
                score += 1
            screen.blit(mini_coin_img, (111 + 94, 10))
            draw_text(f"x {score}", font_score, color_white, 111 + 94 + 25, 5)

        blob_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)

        game_over = player.update(game_over)
        # draw_grid()

        if game_over == -1:
            if restart_button.draw():
                if level == 1:
                    coordinates = (50, screen_height - 120)

                    coin = Coin(14 * tile_size + (tile_size // 2), 11 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(8 * tile_size + (tile_size // 2), 6 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(9 * tile_size + (tile_size // 2), 1 * tile_size + 16)
                    coin_group.add(coin)

                if level == 2:
                    coordinates = (50, 50)

                    coin = Coin(14 * tile_size + (tile_size // 2), 7 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(4 * tile_size + (tile_size // 2), 8 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(17 * tile_size + (tile_size // 2), 12 * tile_size + 16)
                    coin_group.add(coin)

                player.reset(*coordinates)
                game_over = 0
                score = 0

        if game_over == 1:
            pygame.draw.rect(screen, color_brown, (screen_width // 2 - 200, screen_height // 2 - 200,
                                                   screen_width // 2 + 50, screen_height // 2 + 50))
            pygame.draw.rect(screen, color_brown_dark, (screen_width // 2 - 200, screen_height // 2 - 200,
                                                        screen_width // 2 + 50, screen_height // 2 + 50), 5)
            if score == 0:
                screen.blit(coin_dark, (screen_width // 2 - 160, screen_height // 2 - 80))
                screen.blit(coin_dark, (screen_width // 2 - 45, screen_height // 2 - 80))
                screen.blit(coin_dark, (screen_width // 2 + 70, screen_height // 2 - 80))
            elif score == 1:
                screen.blit(coin_img, (screen_width // 2 - 160, screen_height // 2 - 80))
                screen.blit(coin_dark, (screen_width // 2 - 45, screen_height // 2 - 80))
                screen.blit(coin_dark, (screen_width // 2 + 70, screen_height // 2 - 80))
            elif score == 2:
                screen.blit(coin_img, (screen_width // 2 - 160, screen_height // 2 - 80))
                screen.blit(coin_img, (screen_width // 2 - 45, screen_height // 2 - 80))
                screen.blit(coin_dark, (screen_width // 2 + 70, screen_height // 2 - 80))
            elif score == 3:
                screen.blit(coin_img, (screen_width // 2 - 160, screen_height // 2 - 80))
                screen.blit(coin_img, (screen_width // 2 - 45, screen_height // 2 - 80))
                screen.blit(coin_img, (screen_width // 2 + 70, screen_height // 2 - 80))

            continue_img = pygame.transform.scale(continue_img, (96 * 2, 32 * 2))
            complete = Button(screen_width // 2 - 90, screen_height // 2 + 100, continue_img)
            if restart_button.draw():
                if level == 1:
                    coordinates = (50, screen_height - 120)

                    coin = Coin(14 * tile_size + (tile_size // 2), 11 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(8 * tile_size + (tile_size // 2), 6 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(9 * tile_size + (tile_size // 2), 1 * tile_size + 16)
                    coin_group.add(coin)
                if level == 2:
                    coordinates = (50, 50)

                    coin = Coin(14 * tile_size + (tile_size // 2), 7 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(4 * tile_size + (tile_size // 2), 8 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(17 * tile_size + (tile_size // 2), 12 * tile_size + 16)
                    coin_group.add(coin)

                player.reset(*coordinates)
                game_over = 0
                score = 0

            if complete.draw():
                main_menu = True
                exit_button_main.draw()
                if level == 1:
                    coordinates = (50, screen_height - 120)

                    coin = Coin(14 * tile_size + (tile_size // 2), 11 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(8 * tile_size + (tile_size // 2), 6 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(9 * tile_size + (tile_size // 2), 1 * tile_size + 16)
                    coin_group.add(coin)
                    f = open("res/levels.txt", "r")
                    a = str(f.read())
                    # print(a)
                    if score > int(a[0]):
                        a = str(score) + a[1:]
                        # print(a)
                    f.close()
                    f = open("res/levels.txt", "w")
                    f.write(a)
                    f.close()

                if level == 2:
                    coordinates = (50, 50)

                    coin = Coin(14 * tile_size + (tile_size // 2), 7 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(4 * tile_size + (tile_size // 2), 8 * tile_size + 16)
                    coin_group.add(coin)
                    coin = Coin(17 * tile_size + (tile_size // 2), 12 * tile_size + 16)
                    coin_group.add(coin)

                    f = open("res/levels.txt", "r")
                    a = str(f.read())
                    # print(a)
                    if score > int(a[2]):
                        a = a[0] + " " + str(score)
                        # print(a)
                    f.close()
                    f = open("res/levels.txt", "w")
                    f.write(a)
                    f.close()

                player.reset(*coordinates)
                game_over = 0
                score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
f.close()
