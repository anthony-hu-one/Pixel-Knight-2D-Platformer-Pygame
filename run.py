import os
import sys
import pygame
import pyganim
import random
import time
import math
from pygame.locals import *
from PIL import Image

# GLOBAL CONSTANTS
# Game Constants
SCREEN_WIDTH = 854
SCREEN_HEIGHT = 480
SCREEN_SIZE = pygame.Rect((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
TILE_SIZE = 32
GRAVITY = pygame.Vector2((0, 1.0))
VOLUME = 0.025
TILE_DICT = {   (0, 0, 0, 255): "foreground_0.png",
                (5, 5, 5, 255): "foreground_1.png",
                (10, 10, 10, 255): "foreground_2.png",
                (15, 15, 15, 255): "floor.png",
                (16, 16, 16, 255): "floor_medium.png",
                (17, 17, 17, 255): "floor_thick.png",
                (20, 20, 20, 255): "floor_right.png",
                (25, 25, 25, 255): "floor_left.png",
                (30, 30, 30, 255): "floor_stop_right.png",
                (35, 35, 35, 255): "floor_stop_left.png",
                (40, 40, 40, 255): "ceiling.png",
                (45, 45, 45, 255): "ceiling_right_inner.png",
                (50, 50, 50, 255): "ceiling_right_outer.png",
                (55, 55, 55, 255): "ceiling_left_inner.png",
                (60, 60, 60, 255): "ceiling_left_outer.png",
                (65, 65, 65, 255): "wall_right.png",
                (70, 70, 70, 255): "wall_left.png",
                (75, 75, 75, 255): "platform.png",
                (80, 80, 80, 255): "platform_right.png",
                (85, 85, 85, 255): "platform_left.png",
                (90, 90, 90, 255): "platform_small.png",
                (245, 245, 245): "background_2.png",
                (250, 250, 250): "background_1.png",
                (255, 255, 255): "background_0.png"





}
# Animation Constants
PLAYING = 'playing'
PAUSED = 'paused'
STOPPED = 'stopped'
TIME_FUNC = lambda: int(time.time() * 1000)


class Game(object):
    """
    A single instance of this class is responsible for
    managing which individual game state is active
    and keeping it updated.
    """

    def __init__(self, screen, states, start_state):
        """
        Initialize the Game object.
        """
        self.done = False
        self.screen = screen
        self._screen = self.screen.copy()
        self._screen_width = 0
        self._screen_height = 0
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]
        self.cutscene = Cutscene()

    def event_loop(self):
        """Events are passed for handling to the current state."""
        for event in pygame.event.get():
            self.state.get_event(event)

            if event.type == VIDEORESIZE:
                self._screen_width = event.w
                self._screen_height = event.h
                if min(event.w, event.h) is event.w:
                    self._screen_height = int(event.w / SCREEN_RATIO)
                else:
                    self._screen_width = int(event.h * SCREEN_RATIO)
                self.screen = pygame.display.set_mode((event.w, event.h), HWSURFACE | DOUBLEBUF | RESIZABLE)

    def flip_state(self):
        """Switch to the next game state."""
        self.state.done = False
        self.state_name = self.state.next_state
        self.state = self.states[self.state_name]
        if type(self.state).__name__ is 'GamePlay':
            self.state.music['main'].play(loops=-1)
        self.state.startup(self.state.persist)

    def update(self, dt):
        """
        Check for state flip and update active state.

        dt: milliseconds since last frame
        """
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()

        self.state.update(dt)

    def draw(self):
        """Pass display surface to active state for drawing."""
        self.state.draw(self._screen)

    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            self.screen.blit(pygame.transform.scale(self._screen, (self._screen_width, self._screen_height)), (0, 0))
            pygame.display.update()


class GameState(object):
    """
    Parent class for individual game states to inherit from.
    """

    def __init__(self):
        self.done = False
        self.quit = False
        self.paused = False
        self.options_open = False
        self.gameover = False
        self.win = False
        self.next_state = None
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.persist = {}
        self.font = pygame.font.Font(os.path.join("resources/font", "boxy_bold.ttf"), 32)

    def startup(self, persistent):
        """
        Called when a state resumes being active.
        Allows information to be passed between states.

        persistent: a dict passed from state to state
        """
        self.persist = persistent

    def get_event(self, event):
        """
        Handle a single event passed by the Game object.
        """
        pass

    def update(self, dt):
        """
        Update the state. Called by the Game object once
        per frame.

        dt: time since last frame
        """
        pass

    def draw(self, surface):
        """
        Draw everything to the screen.
        """
        pass


class Menu(GameState):
    def __init__(self):
        super(Menu, self).__init__()
        self.title = pygame.image.load(os.path.join("resources/images/gui", "title.png"))
        #self.title = self.font.render("Press Any Key to Continue", True, pygame.Color("white"))
        #self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.persist["screen_color"] = "black"
        self.next_state = "GAMEPLAY"

        '''
        Music
        '''
        self.music = pygame.mixer.Sound('resources/sounds/music/menu.ogg')
        self.music.set_volume(0.15)
        self.music.play(loops=-1)

        self.buttons = [Button((100, 360), 'Play Game', 'options', type=('play')),
                        Button((500, 360), 'Options', 'options', type=('enter', 'options'))]

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True

    def update(self, dt):
        if game.cutscene.in_progress:
            game.cutscene.update()
            if game.cutscene.name is 'switch_play':
                if game.cutscene.elapsed_time > 500:
                    self.done = True
        else:
            for button in self.buttons:
                button.get_event()
        options.update()

    def draw(self, surface):
        surface.fill(pygame.Color("black"))
        surface.blit(self.title, (0, 0))
        for button in self.buttons:
            button.draw(surface)
        if self.options_open:
            options.draw(surface)
        if game.cutscene.in_progress:
            surface.blit(game.cutscene.screen_overlay, (0, 0))


class GamePlay(GameState):
    def __init__(self):
        super(GamePlay, self).__init__()

        self.entities  = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies   = pygame.sprite.Group()
        self.items     = pygame.sprite.Group()
        self.doors     = pygame.sprite.Group()
        self.objects   = pygame.sprite.Group()
        self.player = Player(self.platforms, self.enemies, self.items, self.doors, self.objects, (TILE_SIZE, 23 * TILE_SIZE), self.entities)
        self.camera = CameraAwareLayeredUpdates(self.player, pygame.Rect(0, 0, 1, 1), SCREEN_SIZE)
        self.camera.readjust()


        self.level_list = []
        l00 = Level("level_100.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l01 = Level("level_101.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l02 = Level("level_102.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l03 = Level("level_103.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l04 = Level("level_104.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l05 = Level("level_105.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        l06 = Level("level_106.png", self.player, self.platforms, self.enemies, self.items, self.doors, self.objects, self.entities, self.camera)
        self.level_list.append(l00) # level 00 is a throwaway level that makes the list indices for the door system match up
        self.level_list.append(l01)
        self.level_list.append(l02)
        self.level_list.append(l03)
        self.level_list.append(l04)
        self.level_list.append(l05)
        self.level_list.append(l06)

        self.current_level_number = 1
        self.current_level = self.level_list[self.current_level_number]
        self.camera.level_size = pygame.Rect(0, 0, self.current_level.width, self.current_level.height)
        self.change_level(self.current_level_number, self.player.rect.center)

        self.next_state = "MENU"

        self.darken_screen = pygame.image.load(os.path.join("resources/images/gui", "darken.png")).convert()
        self.pause_screen = pygame.image.load(os.path.join("resources/images/gui", "pause.png")).convert()
        self.gameover_screen = pygame.image.load(os.path.join("resources/images/gui", "game_over.png")).convert_alpha()
        self.win_screen = pygame.image.load(os.path.join("resources/images/gui", "win.png")).convert_alpha()

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['pause'] = [pygame.mixer.Sound('resources/sounds/ui/pause_in.wav')]
        self.sounds['unpause'] = [pygame.mixer.Sound('resources/sounds/ui/pause_out.wav')]

        '''
        Music
        '''
        self.music = {}
        self.music['main'] = pygame.mixer.Sound('resources/sounds/music/main.ogg')
        self.music['gameover'] = pygame.mixer.Sound('resources/sounds/music/gameover.ogg')
        self.music['win'] = pygame.mixer.Sound('resources/sounds/music/win.ogg')
        self.music['main'].set_volume(0.05)
        self.music['gameover'].set_volume(0.15)
        self.music['win'].set_volume(0.15)

        self.buttons = [Button((300, 280), 'Options', 'options', type=('enter', 'options')),
                        Button((300, 360), 'Quit Game', 'options', type=('quit')),
                        Button((300, 320), 'Back to Menu', 'options', type=('menu'))]

        self.button_end = Button((300, 280), 'Quit Game', 'options', type=('quit'))

    def startup(self, persistent):
        self.persist = persistent

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYDOWN:
            if not self.gameover:
                if not self.options_open:
                    if event.key == pygame.K_ESCAPE:
                        audioPlayback(self.sounds['pause'])
                        self.paused = not self.paused
                        if self.paused:
                            pygame.mixer.pause()
                        elif not self.paused:
                            audioPlayback(self.sounds['unpause'])
                            pygame.mixer.unpause()

    def update(self, dt):
        if not self.paused:
            if not self.gameover:
                if not self.win:
                    self.camera.update(self.current_level.entities)
                    if game.cutscene.in_progress:
                        game.cutscene.update()
        if game.cutscene.in_progress:
            if game.cutscene.name is 'switch_menu':
                game.cutscene.update()
                if game.cutscene.elapsed_time > 200:
                    pygame.mixer.stop()
                    self.paused = False
                    self.done = True

        if self.win or self.gameover:
            self.button_end.get_event()

        if self.paused:
            options.update()
            for button in self.buttons:
                button.get_event()

    def change_level(self, level_number, level_pos):
        self.current_level_number = level_number
        self.current_level = self.level_list[self.current_level_number]
        self.player.rect.center = level_pos
        self.player.platforms = self.current_level.platforms
        self.player.enemies = self.current_level.enemies
        self.player.items = self.current_level.items
        self.player.doors = self.current_level.doors
        self.player.objects = self.current_level.objects
        self.camera.level_size = pygame.Rect(0, 0, self.current_level.width, self.current_level.height)
        self.camera.readjust()
        for enemy in self.enemies:
            enemy.platforms = self.current_level.platforms
            enemy.objects = self.current_level.objects

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.camera.draw(surface)
        if self.paused:
            surface.blit(self.darken_screen, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(self.pause_screen, (0, 0))
            for button in self.buttons:
                button.draw(surface)
        if game.cutscene.in_progress:
            surface.blit(game.cutscene.screen_overlay, (0, 0))
        if self.options_open:
            options.draw(surface)
        if self.gameover:
            surface.blit(self.gameover_screen, (0, 0))
        if self.win:
            surface.blit(self.win_screen, (0, 0))
        if self.win or self.gameover:
            self.button_end.draw(surface)

class Cutscene(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.elapsed_time = 0
        self.duration = 0
        self.in_progress = False
        self.fade_in_duration = 0
        self.fade_out_duration = 0
        self.fade_in_start = 0
        self.fade_out_start = 0
        self.alpha = 0
        self.screen_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_overlay.fill((0, 0, 0))
        self.screen_overlay.set_alpha(self.alpha)

    def update(self):
        dt = game.clock.tick(game.fps)
        self.elapsed_time += dt
        if self.duration > 0:
            if self.elapsed_time > self.duration:
                self.end()
            if self.fade_out_duration > 0:
                if self.fade_out_start < self.elapsed_time < self.fade_out_duration + self.fade_out_start:
                    self.fade_out(self.elapsed_time)
                elif self.elapsed_time < self.fade_out_start:
                    self.alpha = 0
                    self.screen_overlay.set_alpha(self.alpha)
            if self.fade_in_duration > 0:
                if self.fade_in_start < self.elapsed_time < self.duration - self.fade_in_duration:
                    self.fade_in(self.elapsed_time)


    def start(self, duration=-1, fadeout=0, fadein=0, fadeout_start=0, fadein_start=0, name=None):
        # duration=-1 means the length of the cutscene is unlimited
        # all the fade parameters are durations whose sum can exceed the duration parameter
        #
        # naturally only one cutscene can play at a time so running this
        # function again while a cutscene is still active will replace the
        # active cutscene with a new one
        self.reset()
        self.name = name

        if duration < 0:
            duration = -1

        fadetime = fadein_start + fadein + fadeout_start + fadeout
        self.fade_in_duration = fadein
        self.fade_out_duration = fadeout
        if fadetime > duration:
            self.duration = fadetime
        else:
            self.duration = duration
        if fadein > 0:
            if fadein_start == 0:
                self.fade_in_start = self.duration - self.fade_in_duration
            else:
                self.fade_in_start = fadein_start
        self.fade_out_start = fadeout_start

        # exception handling
        # if any negative values are passed for the fade parameters, do not start the cutscene
        if True in [True for i in [fadeout, fadein, fadeout_start, fadein_start] if i < 0]:
            self.reset()
            self.in_progress = False

        self.in_progress = True

    def end(self):
        self.reset()

    def fade_in(self, elapsed):
        self.alpha = 255 - int((elapsed - self.fade_in_start)/ (self.fade_in_duration / 255))
        self.screen_overlay.set_alpha(self.alpha)

    def fade_out(self, elapsed):
        self.alpha = int((elapsed - self.fade_out_start)/ (self.fade_out_duration / 255))
        self.screen_overlay.set_alpha(self.alpha)

    def pixelate_fade_in(self):
        pass

    def pixelate_fade_out(self):
        pass


class CameraAwareLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, target, level_size, screen_size):
        super().__init__()
        self.target = target
        self.camera = pygame.Vector2(0, 0)
        self.level_size = level_size
        self.screen_size = screen_size
        if self.target:
            self.add(target)
        self.lostSprites = []
        self.active_sprites = []
        vignette = pygame.image.load(os.path.join("resources/images/misc", "vignette.png")).convert_alpha()
        self.vignette = pygame.transform.scale(vignette, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.Font(os.path.join("resources/font", "boxy_bold.ttf"), 20)
        self.ui_health = Animation(os.path.join("resources/images/gui", "health.png"), rows=14, cols=1, loop=False)
        self.ui_score = self.font.render("- SCORE -", True, pygame.Color("white"))
        self.ui_score_value = self.font.render("00000000", True, pygame.Color("white"))
        self.ui_key = pygame.image.load(os.path.join("resources/images/gui", "key.png")).convert_alpha()
        self.ui_key = pygame.transform.scale(self.ui_key, (64, 64))

    def update(self, active_sprites):
        self.active_sprites = []
        self.active_sprites = active_sprites
        for s in self.sprites():
            if s in self.active_sprites:
                s.update()
        if self.target:
            if type(self.target).__name__ is 'Player':
                self.target.update()
            x = -self.target.rect.center[0] + self.screen_size.width/2
            y = -self.target.rect.center[1] + self.screen_size.height/2
            self.camera += (pygame.Vector2((x, y)) - self.camera) * 0.05
            self.camera.x = max(-(self.level_size.width - self.screen_size.width), min(0, self.camera.x))
            self.camera.y = max(-(self.level_size.height - self.screen_size.height), min(0, self.camera.y))
            self.ui_score_value = self.font.render(str(self.target.score).zfill(8), True, pygame.Color("white"))

    def readjust(self):
        if self.target:
            old_camera_x = self.camera.x
            old_camera_y = self.camera.y
            x = -self.target.rect.center[0] + self.screen_size.width/2
            y = -self.target.rect.center[1] + self.screen_size.height/2
            self.camera += (pygame.Vector2((x, y)) - self.camera) * 0.05
            self.camera.x = max(-(self.level_size.width - self.screen_size.width), min(0, self.camera.x))
            self.camera.y = max(-(self.level_size.height - self.screen_size.height), min(0, self.camera.y))
            new_camera_x = self.camera.x
            new_camera_y = self.camera.y
            dx = old_camera_x - new_camera_x
            dy = old_camera_y - new_camera_y
            if dx != 0 or dy != 0:
                self.readjust()

    def draw(self, surface):
        self.lostSprites = []

        background = game.state.level_list[game.state.current_level_number].background
        background = surface.blit(background.image, background.rect.move(self.camera))
        self.lostSprites.append(background)
        for sprite in self.sprites():
            if sprite in self.active_sprites:
                if type(sprite).__name__ is 'Door':
                    self.spriteblit(sprite, surface)
                if type(sprite).__class__.__bases__[0].__name__ is 'Item':
                    self.spriteblit(sprite, surface)
        for sprite in sorted(self.sprites(), key=self.sort_by_x):
            if sprite in self.active_sprites or type(sprite).__name__ is 'Player':
                if type(sprite).__name__ not in ['Door']:
                    if type(sprite).__class__.__bases__[0].__name__ not in ['Item']:
                        self.spriteblit(sprite, surface)
        foreground = game.state.level_list[game.state.current_level_number].foreground
        foreground = surface.blit(foreground.image, foreground.rect.move(self.camera))
        self.lostSprites.append(foreground)
        surface.blit(self.vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(self.ui_health.getFrame(self.target.health), (16, 16))
        surface.blit(self.ui_score, (600, 16))
        surface.blit(self.ui_score_value, (602, 48))
        if self.target.key:
            surface.blit(self.ui_key, (782, 4))

        return self.lostSprites

    def spriteblit(self, sprite, surface):
        rect = self.spritedict[sprite]
        newrect = surface.blit(sprite.image, sprite.rect.move(self.camera).move(sprite.offset))
        if rect is self._init_rect:
            self.lostSprites.append(newrect)
        else:
            if newrect.colliderect(rect):
                self.lostSprites.append(newrect.union(rect))
            else:
                self.lostSprites.append(newrect)
                self.lostSprites.append(rect)
        self.spritedict[sprite] = newrect

    def sort_by_x(self, sprite):
        return -sprite.rect.centerx


def build_layer(level):
    # construct an image layer for a level
    image = Image.open(level)
    pixel = image.load()
    width = (TILE_SIZE * int(image.size[0]))
    height = (TILE_SIZE * int(image.size[1]))
    layer = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if pixel[i, j] in TILE_DICT.keys():
                tile = pygame.image.load(os.path.join("resources/images/tiles", TILE_DICT[pixel[i, j]]))
                tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                layer.blit(tile, (i * TILE_SIZE, j * TILE_SIZE))

    return layer


class Level(object):
    def __init__(self, level, player, platforms, enemies, items, doors, objects, entities, camera):
        image = Image.open(os.path.join("resources/images/levels", level))
        pixel = image.load()
        self.width  = image.size[0] * TILE_SIZE
        self.height = image.size[1] * TILE_SIZE
        self.entities  = []
        self.platforms = []
        self.enemies   = []
        self.items     = []
        self.doors     = []
        self.objects   = []
        self.background = Background(level, self.width, self.height, entities, camera)
        self.foreground = Foreground(level, self.width, self.height, entities, camera)

        for i in range(image.size[0]):
            for j in range(image.size[1]):
                if pixel[i, j][1] == 248:
                    door = Door(player, pixel[i, j][0], pixel[i, j][2], (i * TILE_SIZE, j * TILE_SIZE), doors, entities, camera)
                    self.entities.append(door)
                    self.doors.append(door)
                if pixel[i, j] == (128, 0, 255):
                    gate = Gate(player, (i * TILE_SIZE, j * TILE_SIZE), objects, entities, camera)
                    self.entities.append(gate)
                    self.objects.append(gate)
                if pixel[i, j] == (0, 0, 0):
                    platform = Platform((i * TILE_SIZE, j * TILE_SIZE), platforms, entities, camera)
                    self.entities.append(platform)
                    self.platforms.append(platform)
                if pixel[i, j] == (20, 20, 20):
                    platform = Platform((i * TILE_SIZE, j * TILE_SIZE), platforms, entities, camera, type='upper')
                    self.entities.append(platform)
                    self.platforms.append(platform)
                if pixel[i, j] == (255, 128, 0):
                    enemy = Snake(player, platforms, enemies, objects, (i * TILE_SIZE, j * TILE_SIZE), enemies, entities, camera)
                    self.entities.append(enemy)
                    self.enemies.append(enemy)
                if pixel[i, j] == (128, 64, 0):
                    enemy = Rat(player, platforms, enemies, objects, (i * TILE_SIZE, j * TILE_SIZE), enemies, entities, camera)
                    self.entities.append(enemy)
                    self.enemies.append(enemy)
                if pixel[i, j] == (255, 216, 0):
                    item = Coin(player, platforms, (i * TILE_SIZE, j * TILE_SIZE), items, entities, camera)
                    self.entities.append(item)
                    self.items.append(item)
                if pixel[i, j] == (0, 0, 255):
                    item = Key(player, platforms, (i * TILE_SIZE, j * TILE_SIZE), items, entities, camera)
                    self.entities.append(item)
                    self.items.append(item)
                if pixel[i, j] == (0, 255, 255):
                    item = Diamond(player, platforms, (i * TILE_SIZE, j * TILE_SIZE), items, entities, camera)
                    self.entities.append(item)
                    self.items.append(item)
                if pixel[i, j] == (255, 0, 0):
                    item = Heart(player, platforms, (i * TILE_SIZE, j * TILE_SIZE), items, entities, camera)
                    self.entities.append(item)
                    self.items.append(item)


        # self.entities.append(player)


class Entity(pygame.sprite.Sprite):
    def __init__(self, color, pos, *groups):
        super().__init__()

        self.pos = pygame.Vector2(pos)
        self.facing = None
        self.animations = {}
        self.offsets = {}

        self.__g = {}  # The groups the sprite is in
        if groups:
            self.add(*groups)

        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.imagerect = self.image.get_rect(topleft=pos)
        self.offset = pygame.Vector2(0, 0)

    def add(self, *groups):
        """
        Add the sprite to groups

        Any number of Group instances can be passed as arguments. The
        Sprite will be added to the Groups it is not already a member of.
        """
        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, '_spritegroup'):
                if not has(group):
                    group.add_internal(self)
                    self.add_internal(group)

    def set_animation(self, key):
        if self.facing == 'R':
            self.image = pygame.transform.flip(self.animations[key].getCurrentFrame(), 1, 0)
        if self.facing == 'L':
            self.image = self.animations[key].getCurrentFrame()
        self.offset = self.offsets[key][self.facing]
        self.imagerect = self.image.get_rect(topleft=self.rect.topleft)


class Player(Entity):
    def __init__(self, platforms, enemies, items, doors, objects, pos, *groups):
        super().__init__(Color("#AAAAAA"), pos)
        self.vel = pygame.Vector2((0, 0))
        self.onGround = False
        self.platforms = platforms
        self.enemies = enemies
        self.items = items
        self.doors = doors
        self.speed = TILE_SIZE * 5 / 32
        self.jump_strength = math.sqrt(TILE_SIZE / 32) * 14
        self.facing = 'L'

        self.alive = True
        self.health = 13
        self.lives = 3
        self.score = 0
        self.key = False
        self.attack_time = 0
        self.attack_combo_time = 0
        self.hurt_time = 0
        self.death_time = 12

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['step'] = [pygame.mixer.Sound('resources/sounds/entities/player/footstep00.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep01.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep02.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep03.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep04.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep05.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep06.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep07.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep08.ogg'),
                               pygame.mixer.Sound('resources/sounds/entities/player/footstep09.ogg')]
        self.sounds['attack'] = [pygame.mixer.Sound('resources/sounds/entities/player/attack1.wav')]
        self.sounds['hit'] = [pygame.mixer.Sound('resources/sounds/entities/player/hit.wav')]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/player_idle.png", rows=4, cols=1, frameTime=150)
        self.animations['idle'].play()
        self.animations['walking'] = Animation("resources/images/entities/player_walking.png", rows=8, cols=1, frameTime=100)
        self.animations['walking'].play()
        self.animations['jumping'] = Animation("resources/images/entities/player_jumping.png", rows=1, cols=1)
        self.animations['falling'] = Animation("resources/images/entities/player_falling.png", rows=1, cols=1)
        self.animations['attacking_high'] = Animation("resources/images/entities/player_attacking_high.png", rows=3, cols=1, frameTime=150, loop=False)
        self.animations['attacking_low'] = Animation("resources/images/entities/player_attacking_low.png", rows=3, cols=1, frameTime=150, loop=False)
        self.animations['death'] = Animation("resources/images/entities/player_death.png", rows=6, cols=1, frameTime=100, loop=False)

        '''
        Animation Offsets
        '''
        self.offsets = {}
        self.offsets['idle'] = {'L': pygame.Vector2(-24, -4), 'R': pygame.Vector2(-8, -4)}
        self.offsets['walking'] = {'L': pygame.Vector2(-24, -4), 'R': pygame.Vector2(0, -4)}
        self.offsets['jumping'] = {'L': pygame.Vector2(-40, -4), 'R': pygame.Vector2(-8, -4)}
        self.offsets['falling'] = {'L': pygame.Vector2(-40, -4), 'R': pygame.Vector2(-8, -4)}
        self.offsets['attacking_high'] = {'L': pygame.Vector2(-64, -16), 'R': pygame.Vector2(-32, -16)}
        self.offsets['attacking_low'] = {'L': pygame.Vector2(-64, -16), 'R': pygame.Vector2(-32, -16)}
        self.offsets['death'] = {'L': pygame.Vector2(-32, -12), 'R': pygame.Vector2(-32, -12)}

        self.image = self.animations['idle'].getCurrentFrame()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.inflate_ip(-32, -4)

    def update(self):
        dt = game.clock.tick(game.fps)

        if game.cutscene.in_progress:
            self.vel.x = 0
        if not game.cutscene.in_progress:
            pressed = pygame.key.get_pressed()

            if self.health > 0:
                if pressed[K_w]:
                    door_hit_list = pygame.sprite.spritecollide(self, self.doors, False)
                    # only jump if on the ground
                    # and if not attacking
                    # and if not in front of a door
                    if self.onGround and self.attack_time == 0 and not door_hit_list:
                        self.vel.y = -self.jump_strength
                    if self.vel.y < 0:
                        if self.attack_time == 0:
                            self.set_animation('jumping')
                    # doors logic
                    if door_hit_list:
                        if door_hit_list[0] in game.state.level_list[game.state.current_level_number].doors:
                            if (door_hit_list[0].rect.centerx > self.rect.centerx and self.facing is 'R') or (door_hit_list[0].rect.centerx < self.rect.centerx and self.facing is 'L'):
                                self.usedoor(door_hit_list[0])

                if pressed[K_a]:
                    self.vel.x = -self.speed
                    self.facing = 'L'
                    if self.onGround:
                        if self.attack_time == 0:
                            self.set_animation('walking')
                            if self.animations['walking'].currentFrameNum in [0, 4]:
                                audioPlayback(self.sounds['step'])
                if pressed[K_d]:
                    self.vel.x = self.speed
                    self.facing = 'R'
                    if self.onGround:
                        if self.attack_time == 0:
                            self.set_animation('walking')
                            if self.animations['walking'].currentFrameNum in [0, 4]:
                                audioPlayback(self.sounds['step'])
                if pressed[K_SPACE]:
                    if self.attack_time == 0:
                        self.attack_time = 20
                        if self.attack_combo_time == 0:
                            self.animations['attacking_high'].play()
                            audioPlayback(self.sounds['attack'])
                        elif self.attack_combo_time > 0:
                            self.animations['attacking_low'].play()
                            audioPlayback(self.sounds['attack'])
                            self.attack_combo_time = -1
                if not(pressed[K_a] or pressed[K_d]):
                    self.vel.x = 0
                    if self.onGround:
                        if self.attack_time == 0:
                            self.set_animation('idle')
                # run attacks
                if self.attack_time != 0 or self.attack_combo_time != 0:
                    self.attack(dt)
                # highlight closest gate in range for interaction
                gates = [i for i in self.objects if
                         type(i).__name__ is 'Gate' and spritedistance(i, self) <= TILE_SIZE * 2]
                if gates:
                    gates = sorted(gates, key=lambda e: spritedistance(e, self))
                    gates[0].selected = True
                    for gate in gates[1:]:
                        gate.selected = False
                # unlock gates
                if pressed[K_e]:
                    if self.key:
                        if gates:
                            if gates[0]:
                                if gates[0].selected and gates[0].locked:
                                    gates[0].unlock()
                                    self.key = False
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.vel += GRAVITY
            if self.vel.y > 1:
                if self.attack_time == 0:
                    self.set_animation('falling')
        if self.health == 0 and self.alive and self.onGround:
            self.death()
        # increment in x direction
        self.rect.left += self.vel.x
        # do x-axis collisions
        self.collide(self.vel.x, 0, self.platforms)
        self.collide(self.vel.x, 0, self.objects)
        # assuming the player is in the air
        self.onGround = False
        # increment in y direction
        self.rect.top += self.vel.y
        # do y-axis collisions
        self.collide(0, self.vel.y, self.platforms)
        # check damage and apply red tint
        if self.hurt_time > 0:
            self.red_tint()

    def collide(self, xvel, yvel, group):
        collide_hit_list = pygame.sprite.spritecollide(self, group, False)
        for collision in collide_hit_list:
            if xvel > 0:
                self.rect.right = collision.rect.left
            if xvel < 0:
                self.rect.left = collision.rect.right
            if yvel > 0:
                self.rect.bottom = collision.rect.top
                self.onGround = True
                self.vel.y = 0
                if yvel > 5:
                    audioPlayback(self.sounds['step'])
            if yvel < 0:
                self.rect.top = collision.rect.bottom
                self.vel.y = 0

    def attack(self, dt):
        # animation logic
        if self.attack_time > 0:
            if self.attack_combo_time >= 0:
                self.set_animation('attacking_high')
            if self.attack_combo_time == -1:
                self.set_animation('attacking_low')
            if self.attack_time :
                if self.attack_combo_time == 0:
                    self.attack_combo_time = 6
            self.attack_time -= 1
            self.vel.x = 0

        # damage enemy logic
            if self.attack_time > 8:
                enemy_hit_list = imagecollide(self, self.enemies)
                for enemy in enemy_hit_list:
                    enemy.damage()

        # combo logic
        if self.attack_combo_time != 0:
            if self.attack_combo_time > 0:
                self.attack_combo_time -= 1
            if self.attack_combo_time < 0:
                if self.attack_time == 0:
                    self.attack_combo_time = 0

    def damage(self):
        if not game.cutscene.in_progress:
            if self.hurt_time is 0:
                if self.health > 0:
                    self.health -= 1
                    audioPlayback(self.sounds['hit'])
                    self.hurt_time = 40
                    if self.vel.y == 0:
                        self.vel.y -= 3

    def red_tint(self):
        self.hurt_time -= 1
        _damage = self.image.copy().convert_alpha()
        damage = _damage.copy().convert_alpha()
        damage.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _damage.blit(damage, (0, 0))
        if self.hurt_time >= 15:
            self.image = _damage

    def death(self):
        # play death animation
        self.vel.x = 0
        self.set_animation('death')
        if self.death_time > 0:
            self.death_time -= 1
        if self.death_time % 2 == 0:
            self.animations['death'].nextFrame()
        if self.death_time == 0:
            self.death_time = 12
            self.alive = False
            game.state.gameover = True
            pygame.mixer.stop()
            game.state.music['gameover'].play()

    def usedoor(self, door):
        destination_door  = None
        destination_pos   = None
        destination_level = None
        doors = [i.doors for i in game.state.level_list]
        for each_level in doors:
            for dest_door in each_level:
                if dest_door.id == door.travel_to_id:
                    destination_door = dest_door
        if destination_door:
            destination_level = next(i for i, v in enumerate(game.state.level_list) if destination_door in v.doors)
            destination_pos = destination_door.rect.center
            door.use(destination_level, destination_pos)


class Platform(Entity):
    def __init__(self, pos, *groups, type='full'):
        super().__init__(Color("#DDDDDD"), pos, *groups)

        self.image.set_alpha(0)

        if type == 'upper':
            self.rect = pygame.Rect.inflate(self.rect, (0, -int(TILE_SIZE / 2)))
            self.rect = pygame.Rect.move(self.rect, (0, -int(TILE_SIZE / 4)))


class Door(Entity):
    def __init__(self, player, id, travel_to_id, pos, *groups):
        super().__init__(Color("#DDDDDD"), pos, *groups)
        self.id = id
        self.travel_to_id = travel_to_id
        self.destination_level = None
        self.destination_pos = None
        self.selected = False

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['open'] = [pygame.mixer.Sound("resources/sounds/entities/doors/open0.ogg"),
                               pygame.mixer.Sound("resources/sounds/entities/doors/open1.ogg")]
        self.sounds['close'] = [pygame.mixer.Sound("resources/sounds/entities/doors/close0.ogg"),
                                pygame.mixer.Sound("resources/sounds/entities/doors/close1.ogg"),
                                pygame.mixer.Sound("resources/sounds/entities/doors/close2.ogg"),
                                pygame.mixer.Sound("resources/sounds/entities/doors/close3.ogg")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['open'] = Animation("resources/images/tiles/door.png", rows=4, cols=1, frameTime=150, loop=False)

        self.set_frame(0)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        if not game.cutscene.in_progress:
            self.set_frame(0)

        if game.cutscene.in_progress:
            if self.selected:
                if 0 < game.cutscene.elapsed_time < 50:
                    self.set_frame(1)
                if 50 < game.cutscene.elapsed_time < 100:
                    self.set_frame(2)
                if 100 < game.cutscene.elapsed_time < 150:
                    self.set_frame(3)
                if self.destination_level and self.destination_pos:
                    if game.cutscene.elapsed_time > 400:
                        audioPlayback(self.sounds['close'])
                        self.set_frame(0)
                        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 2))
                        game.state.change_level(self.destination_level, self.destination_pos)
                        self.destination_level = None
                        self.destination_pos = None
                        self.selected = False


    def use(self, level, pos):
        self.destination_level = level
        self.destination_pos = pos
        self.selected = True
        audioPlayback(self.sounds['open'])
        game.cutscene.start(fadeout=200, fadein=200, fadeout_start=200, fadein_start=500)

    def set_frame(self, index):
        self.image = self.animations['open'].getFrame(index)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 2))


class Gate(Entity):
    def __init__(self, player, pos, *groups):
        super().__init__(Color("#DDDDDD"), pos, *groups)
        self.locked = True
        self.open = False
        self.selected = False
        self.played_sound = False
        self.player = player

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['unlock'] = [pygame.mixer.Sound("resources/sounds/entities/objects/gate_unlock.ogg")]
        self.sounds['open'] = [pygame.mixer.Sound("resources/sounds/entities/objects/gate_open.ogg")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/tiles/gate_locked.png", rows=1, cols=1, frameTime=150, loop=False)
        self.animations['interact'] = Animation("resources/images/tiles/gate_interact.png", rows=1, cols=2, frameTime=200, loop=True)
        self.animations['interact'].play()
        self.animations['unlock'] = Animation("resources/images/tiles/gate_unlock.png", rows=1, cols=9, frameTime=75, loop=False)
        self.animations['open'] = Animation("resources/images/tiles/gate_open.png", rows=1, cols=8, frameTime=150, loop=False)

        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))
        self.rect = self.image.get_rect(topleft=pos)
        self.rect = self.rect.inflate((int(-TILE_SIZE), 0))
        self.rect = self.rect.move((int(TILE_SIZE), 0))
        self.offset = pygame.Vector2(-int(TILE_SIZE // 2), 0)

    def update(self):
        if self.locked:
            if self.player.key:
                if self.selected:
                    if spritedistance(self, self.player) <= TILE_SIZE * 2:
                        self.image = self.animations['interact'].getCurrentFrame()
                        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))
                    else:
                        self.selected = False
                        self.image = self.animations['idle'].getCurrentFrame()
                        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))
            else:
                self.selected = False
                self.image = self.animations['idle'].getCurrentFrame()
                self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))

        if not self.locked:
            if not self.open:
                if self.selected:
                    if game.cutscene.in_progress:
                        if 0 < game.cutscene.elapsed_time < 200:
                            frnum = int((game.cutscene.elapsed_time / 200) * 9)
                            self.image = self.animations['unlock'].getFrame(frnum)
                            self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))
                        if 200 < game.cutscene.elapsed_time < 450:
                            if not self.played_sound:
                                audioPlayback(self.sounds['open'])
                                self.played_sound = True
                            self.animations['open'].play()
                            frnum = int(((game.cutscene.elapsed_time - 200) / 250) * 8)
                            self.image = self.animations['open'].getFrame(frnum)
                            self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))
                        if 450 < game.cutscene.elapsed_time < 500:
                            self.open = True
                            game.cutscene.end()


    def set_frame(self, animation, index):
        self.image = self.animations[animation].getFrame(index)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE * 3))

    def unlock(self):
        self.locked = False
        self.animations['unlock'].play()
        audioPlayback(self.sounds['unlock'])
        game.cutscene.start(duration=500)
        game.state.level_list[game.state.current_level_number].objects.remove(self)


class Layer(Entity):
    def __init__(self, *groups):
        super().__init__(Color("#000000"), (0, 0), *groups)


class Background(Layer):
    def __init__(self, level, level_width, level_height, *groups):
        super().__init__(*groups)
        if os.path.isfile(os.path.join("resources/images/levels/background", level)):
            self.image = build_layer(os.path.join("resources/images/levels/background", level))
        self.rect = self.image.get_rect()


class Foreground(Layer):
    def __init__(self, level, level_width, level_height, *groups):
        super().__init__(*groups)
        if os.path.isfile(os.path.join("resources/images/levels/foreground", level)):
            self.image = build_layer(os.path.join("resources/images/levels/foreground", level))
        self.rect = self.image.get_rect()


class Enemy(Entity):
    def __init__(self, player, platforms, enemies, objects, pos, *groups):
        super().__init__(Color("#FFFFFF"), pos, *groups)
        self.vel = pygame.Vector2((0, 0))
        self.onGround = False
        self.platforms = platforms
        self.enemies = enemies
        self.player = player
        self.objects = objects
        self.speed = 0
        self.jump_strength = 0
        self.health = 1
        self.aggro_range = 0
        self.facing = None
        self.hurt_time = 0
        self.attack_time = 0

    def collide(self, xvel, yvel, group):
        collide_hit_list = pygame.sprite.spritecollide(self, group, False)
        for collision in collide_hit_list:
            if xvel > 0:
                self.rect.right = collision.rect.left
            if xvel < 0:
                self.rect.left = collision.rect.right
            if yvel > 0:
                self.rect.bottom = collision.rect.top
                self.onGround = True
                self.vel.y = 0
            if yvel < 0:
                self.rect.top = collision.rect.bottom
                self.vel.y = 0

    def chase(self):
        if game.cutscene.in_progress:
            self.vel.x = 0
        if random.randint(1, 10) is 10 and not game.cutscene.in_progress:
            if self.player.rect.x < self.rect.x:
                self.vel.x = -self.speed
                self.facing = 'L'
            if self.player.rect.x > self.rect.x:
                self.vel.x = self.speed
                self.facing = 'R'
            if self.player.rect.x == self.rect.x:
                self.vel.x = 0
            if self.player.rect.y < self.rect.y - (self.aggro_range / 2):
                if self.onGround:
                    self.vel.y = -self.jump_strength

    def attack(self):
        # animation logic
        if self.attack_time > 0:
            self.attack_time -= 1

            # damage player logic
            if self.attack_time > 10:
                player_hit = self.imagerect.colliderect(self.player.imagerect)
                if player_hit:
                    self.player.damage()

    def damage(self):
        if self.hurt_time is 0:
            if self.health > 0:
                self.health -= 1
                audioPlayback(self.sounds['hit'])
                self.hurt_time = 20
                self.vel.y -= 3

    def red_tint(self):
        self.hurt_time -= 1
        _damage = self.image.copy().convert_alpha()
        damage = _damage.copy().convert_alpha()
        damage.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _damage.blit(damage, (0, 0))
        if self.hurt_time >= 5:
            self.image = _damage

    def death(self):
        Particle('cloud.png', 250, 0.5, self.rect.center, (0, 0), game.state.entities, game.state.camera)


class Snake(Enemy):
    def __init__(self, player, platforms, enemies, objects, pos, *groups):
        super().__init__(player, platforms, enemies, objects, pos, *groups)
        self.speed = TILE_SIZE * 2 / 32
        self.jump_strength = math.sqrt(TILE_SIZE / 32) * 10
        self.health = 4
        self.aggro_range = 400
        self.facing = 'L'

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['hit'] = [pygame.mixer.Sound("resources/sounds/entities/enemies/hit.wav")]
        self.sounds['death'] = [pygame.mixer.Sound("resources/sounds/entities/enemies/snake_death.ogg")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/snake_idle.png", rows=2, cols=1, frameTime=300)
        self.animations['idle'].play()

        '''
        Animation Offsets
        '''
        self.offsets = {}
        self.offsets['idle'] = {'L': pygame.Vector2(-8, -12), 'R': pygame.Vector2(-4, -12)}

        self.image = self.animations['idle'].getCurrentFrame()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.inflate_ip(-16, -16)
        self.offset = pygame.Vector2(-4, -12)

    def update(self):
        if spritedistance(self, self.player) <= self.aggro_range:
            self.chase()

            if self.attack_time == 0:
                self.attack_time = 30
            if self.attack_time > 0 or self.attack_combo_time != 0:
                if self.hurt_time == 0:
                    self.attack()
        else:
            self.vel.x = 0

        self.set_animation('idle')

        if not self.onGround:
            # only accelerate with gravity if in the air
            self.vel += GRAVITY

        # increment in x direction
        self.rect.left += self.vel.x
        # do x-axis collisions
        self.collide(self.vel.x, 0, self.platforms)
        self.collide(self.vel.x, 0, self.objects)
        # assuming the player is in the air
        self.onGround = False
        # increment in y direction
        self.rect.top += self.vel.y
        # do y-axis collisions
        self.collide(0, self.vel.y, self.platforms)
        # check damage and apply red tint
        if self.hurt_time > 0:
            self.red_tint()
        # check death
        if self.hurt_time <= 10:
            if self.health is 0:
                audioPlayback(self.sounds['death'])
                self.death()
                self.kill()
                self.player.score += 40


class Rat(Enemy):
    def __init__(self, player, platforms, enemies, objects, pos, *groups):
        super().__init__(player, platforms, enemies, objects, pos, *groups)
        self.speed = TILE_SIZE * 2 / 32
        self.jump_strength = math.sqrt(TILE_SIZE / 32) * 10
        self.health = 3
        self.aggro_range = 400
        self.facing = 'L'

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['hit'] = [pygame.mixer.Sound("resources/sounds/entities/enemies/hit.wav")]
        self.sounds['death'] = [pygame.mixer.Sound("resources/sounds/entities/enemies/rat_death.ogg")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/rat_idle.png", rows=1, cols=1, frameTime=300)
        self.animations['idle'].play()

        '''
        Animation Offsets
        '''
        self.offsets = {}
        self.offsets['idle'] = {'L': pygame.Vector2(-8, -12), 'R': pygame.Vector2(-4, -12)}

        self.image = self.animations['idle'].getCurrentFrame()
        self.rect = self.image.get_rect(center=self.pos)
        self.rect.inflate_ip(-16, -16)
        self.offset = pygame.Vector2(-4, -12)

    def update(self):
        if spritedistance(self, self.player) <= self.aggro_range:
            self.chase()

            if self.attack_time == 0:
                self.attack_time = 30
            if self.attack_time > 0 or self.attack_combo_time != 0:
                if self.hurt_time == 0:
                    self.attack()

        self.set_animation('idle')

        if not self.onGround:
            # only accelerate with gravity if in the air
            self.vel += GRAVITY

        # increment in x direction
        self.rect.left += self.vel.x
        # do x-axis collisions
        self.collide(self.vel.x, 0, self.platforms)
        self.collide(self.vel.x, 0, self.objects)
        # assuming the player is in the air
        self.onGround = False
        # increment in y direction
        self.rect.top += self.vel.y
        # do y-axis collisions
        self.collide(0, self.vel.y, self.platforms)
        # check damage and apply red tint
        if self.hurt_time > 0:
            self.red_tint()
        # check death
        if self.hurt_time <= 10:
            if self.health is 0:
                audioPlayback(self.sounds['death'])
                self.death()
                self.kill()
                self.player.score += 30


class Item(Entity):
    def __init__(self, player, platforms, pos, *groups):
        super().__init__(Color("#FFFFFF"), pos, *groups)
        self.vel = pygame.Vector2((0, 0))
        self.onGround = False
        self.platforms = platforms
        self.player = player
        self.speed = 0

    def update(self):
        player_collision = pygame.sprite.collide_rect(self.player.rect, self.rect)
        if player_collision:
            self.pickup()


class Coin(Item):
    def __init__(self, player, platforms, pos, *groups):
        super().__init__(player, platforms, pos, *groups)

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['coin'] = [pygame.mixer.Sound("resources/sounds/entities/items/coin.wav")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/coin.png", rows=9, cols=1, frameTime=100)
        self.animations['idle'].play()

        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

    def update(self):
        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        player_collision = pygame.sprite.collide_rect(self, self.player)
        if player_collision:
            self.pickup()

    def pickup(self):
        self.player.score += 10
        audioPlayback(self.sounds['coin'])
        Particle('star.png', 40, 1, self.pos, (0, 0), game.state.entities, game.state.camera)
        self.kill()


class Key(Item):
    def __init__(self, player, platforms, pos, *groups):
        super().__init__(player, platforms, pos, *groups)

        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['key'] = [pygame.mixer.Sound("resources/sounds/entities/items/key.wav")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/key.png", rows=1, cols=1, frameTime=100)
        self.animations['idle'].play()

        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

    def update(self):
        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        player_collision = pygame.sprite.collide_rect(self, self.player)
        if player_collision:
            self.pickup()

    def pickup(self):
        self.player.key = True
        audioPlayback(self.sounds['key'])
        Particle('star.png', 40, 1, self.pos, (0, 0), game.state.entities, game.state.camera)
        self.kill()


class Heart(Item):
    def __init__(self, player, platforms, pos, *groups):
        super().__init__(player, platforms, pos, *groups)
        '''
        Sounds
        '''
        self.sounds = {}
        self.sounds['health'] = [pygame.mixer.Sound("resources/sounds/entities/items/heart.wav")]

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/heart.png", rows=6, cols=1, frameTime=120)
        self.animations['idle'].play()

        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

    def update(self):
        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        player_collision = pygame.sprite.collide_rect(self, self.player)
        if player_collision:
            if self.player.health < 13:
                self.pickup()

    def pickup(self):
        if self.player.health <= 11:
            self.player.health += 2
        elif self.player.health == 12:
            self.player.health = 13
        audioPlayback(self.sounds['health'])
        Particle('health.png', 40, 1, self.pos, (0, 0), game.state.entities, game.state.camera)
        self.kill()


class Diamond(Item):
    def __init__(self, player, platforms, pos, *groups):
        super().__init__(player, platforms, pos, *groups)

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation("resources/images/entities/diamond.png", rows=4, cols=1, frameTime=200)
        self.animations['idle'].play()

        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE*2, TILE_SIZE*2))

    def update(self):
        self.image = self.animations['idle'].getCurrentFrame()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE*2, TILE_SIZE*2))

        player_collision = pygame.sprite.collide_rect(self, self.player)
        if player_collision:
            self.pickup()

    def pickup(self):
        game.state.win = True
        pygame.mixer.stop()
        game.state.music['win'].play()


class Particle(Entity):
    def __init__(self, particle, speed, size, pos, motion, *groups):
        super().__init__(Color("#FFFFFF"), pos, *groups)
        self.vel = pygame.Vector2(motion)
        self.duration = speed
        self.size = size
        self.elapsed = 0

        game.state.level_list[game.state.current_level_number].entities.append(self)

        '''
        Animations
        '''
        self.animations = {}
        self.animations['idle'] = Animation(os.path.join("resources/images/particles", particle), rows=8, cols=1, frameTime=speed, loop=False)
        self.animations['idle'].play()

        self.image = self.animations['idle'].getCurrentFrame()
        newsize = int(TILE_SIZE * self.size)
        self.image = pygame.transform.scale(self.image, (newsize, newsize))

    def update(self):

        self.image = self.animations['idle'].getCurrentFrame()
        newsize = int(TILE_SIZE * self.size)
        self.image = pygame.transform.scale(self.image, (newsize, newsize))

        if self.animations['idle'].isFinished():
            self.kill()


def spritecollide(sprite, group):
    """
    Find Sprites in a Group that intersect another Sprite
    """
    spritecollide = sprite.rect.colliderect
    return [s for s in group if spritecollide(s.rect) and s is not sprite]


def imagecollide(sprite, group):
    """
    Find Sprites in a Group whose image intersects another Sprite's image
    """
    imagecollide = sprite.imagerect.colliderect
    return [s for s in group if imagecollide(s.imagerect) and s is not sprite]


def spritedistance(sprite, object):
    return math.hypot(sprite.rect.centerx - object.rect.centerx, sprite.rect.centery - object.rect.centery)


class Animation(object):
    def __init__(self, filename, rows=None, cols=None, frameTime=100, loop=True):
        """
        Animation Class grabbed from Pyganim
        """

        # Constructor function for the animation object. Starts off in the PLAYING state.
        #
        # @param frames
        #     A list of tuples for each frame of animation, in one of the following format:
        #       (image_of_frame<pygame.Surface>, duration_in_milliseconds<int>)
        #       (filename_of_image<str>, duration_in_milliseconds<int>)
        #     Note that the images and duration cannot be changed. A new PygAnimation object
        #     will have to be created.
        # @param loop Tells the animation object to keep playing in a loop.

        # create animation frames from sprite sheet
        frames = self.getImagesFromSpriteSheet(filename, rows=rows, cols=cols, frameTime=frameTime)

        # _images stores the pygame.Surface objects of each frame
        self._images = []
        # _durations stores the durations (in milliseconds) of each frame.
        # e.g. [1000, 1000, 2500] means the first and second frames last one second,
        # and the third frame lasts for two and half seconds.
        self._durations = []
        # _startTimes shows when each frame begins. len(self._startTimes) will
        # always be one more than len(self._images), because the last number
        # will be when the last frame ends, rather than when it starts.
        # The values are in milliseconds.
        # So self._startTimes[-1] tells you the length of the entire animation.
        # e.g. if _durations is [1000, 1000, 2500], then _startTimes will be [0, 1000, 2000, 4500]
        self._startTimes = None

        # if the sprites are transformed, the originals are kept in _images
        # and the transformed sprites are kept in _transformedImages.
        self._transformedImages = []

        self._state = STOPPED  # The state is always either PLAYING, PAUSED, or STOPPED
        self._loop = loop  # If True, the animation will keep looping. If False, the animation stops after playing once.
        self._rate = 1.0  # 2.0 means play the animation twice as fast, 0.5 means twice as slow
        self._visibility = True  # If False, then nothing is drawn when the blit() methods are called

        self._playingStartTime = 0 # the time that the play() function was last called. Epoch timestamp in milliseconds.
        self._pausedStartTime = 0 # the time that the pause() function was last called. Epoch timestamp in milliseconds.

        if frames != '_copy':  # ('_copy' is passed for frames by the getCopies() method)
            self.numFrames = len(frames)
            for i in range(self.numFrames):
                # load each frame of animation into _images
                frame = (frames[i][0], int(frames[i][1]))
                if type(frame[0]) == str:
                    frame = (pygame.image.load(frame[0]), frame[1])
                self._images.append(frame[0])
                self._durations.append(frame[1])

            # calculate start times of each frame
            self._startTimes = [0]
            for i in range(self.numFrames):
                self._startTimes.append(self._startTimes[-1] + self._durations[i])
        del frames

    def getImagesFromSpriteSheet(self, filename, rows=None, cols=None, frameTime=100):
        rects = []
        image = pygame.image.load(filename)

        sprite_width = image.get_width() // cols
        sprite_height = image.get_height() // rows

        for y in range(0, image.get_height(), sprite_height):
            if y + sprite_height > image.get_height():
                continue
            for x in range(0, image.get_width(), sprite_width):
                if x + sprite_width > image.get_width():
                    continue

                rects.append((x, y, sprite_width, sprite_height))

        # create a list of Surface objects from the sprite sheet
        surfaces = []
        for rect in rects:
            surf = pygame.Surface((rect[2], rect[3]), 0, image).convert()
            surf.set_colorkey((63, 114, 107))  # background color to turn transparent
            surf.blit(image, (0, 0), rect, pygame.BLEND_RGBA_ADD)
            surfaces.append(surf)
        frames = list(map(lambda i: (i, frameTime), surfaces))
        del image
        del sprite_width
        del sprite_height
        del rects
        return frames

    def reverse(self):
        # Reverses the order of the frames.
        self.elapsed = (self._durations[-1] + self._startTimes[-1]) - self.elapsed
        self._images.reverse()
        self._transformedImages.reverse()
        self._durations.reverse()

    def getCopy(self):
        # Returns a copy of this PygAnimation object, but one that refers to the
        # Surface objects of the original so it efficiently uses memory.
        #
        # NOTE: Messing around with the original Surface objects will affect all
        # the copies. If you want to modify the Surface objects, then just make
        # copies using constructor function instead.
        return self.getCopies(1)[0]

    def getCopies(self, numCopies=1):
        # Returns a list of copies of this PygAnimation object, but one that refers to the
        # Surface objects of the original so it efficiently uses memory.
        #
        # NOTE: Messing around with the original Surface objects will affect all
        # the copies. If you want to modify the Surface objects, then just make
        # copies using constructor function instead.
        retval = []
        for i in range(numCopies):
            newAnim = Animation('_copy', loop=self.loop)
            newAnim._images = self._images[:]
            newAnim._transformedImages = self._transformedImages[:]
            newAnim._durations = self._durations[:]
            newAnim._startTimes = self._startTimes[:]
            newAnim.numFrames = self.numFrames
            retval.append(newAnim)
        return retval

    def blit(self, destSurface, dest=(0, 0)):
        # Draws the appropriate frame of the animation to the destination Surface
        # at the specified position.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param destSurface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, self.elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)

    def getFrame(self, frameNum):
        # Returns the pygame.Surface object of the frameNum-th frame in this
        # animation object. If there is a transformed version of the frame,
        # it will return that one.
        if self._transformedImages == []:
            return self._images[frameNum]
        else:
            return self._transformedImages[frameNum]

    def getCurrentFrame(self):
        # Returns the pygame.Surface object of the frame that would be drawn
        # if the blit() method were called right now. If there is a transformed
        # version of the frame, it will return that one.
        return self.getFrame(self.currentFrameNum)

    def clearTransforms(self):
        # Deletes all the transformed frames so that the animation object
        # displays the original Surfaces/images as they were before
        # transformation functions were called on them.
        #
        # This is handy to do for multiple transformation, where calling
        # the rotation or scaling functions multiple times results in
        # degraded/noisy images.
        self._transformedImages = []

    def makeTransformsPermanent(self):
        self._images = [pygame.Surface(surfObj.get_size(), 0, surfObj) for surfObj in self._transformedImages]
        for i in range(len(self._transformedImages)):
            self._images[i].blit(self._transformedImages[i], (0,0))

    def blitFrameNum(self, frameNum, destSurface, dest):
        # Draws the specified frame of the animation object. This ignores the
        # current playing state.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param frameNum
        #     The frame to draw (the first frame is 0, not 1)
        # @param destSurface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        destSurface.blit(self.getFrame(frameNum), dest)

    def blitFrameAtTime(self, elapsed, destSurface, dest):
        # Draws the frame the is "elapsed" number of seconds into the animation,
        # rather than the time the animation actually started playing.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param elapsed
        #     The amount of time into an animation to use when determining which
        #     frame to draw. blitFrameAtTime() uses this parameter rather than
        #     the actual time that the animation started playing. (In seconds)
        # @param destSurface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.        elapsed = int(elapsed * self.rate)
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)

    def isFinished(self):
        # Returns True if this animation doesn't loop and has finished playing
        # all the frames it has.
        return not self.loop and self.elapsed >= self._startTimes[-1]

    def play(self, startTime=None): # startTime is epoch timestamp in milliseconds. TODO: Change this?
        # Start playing the animation.

        # play() is essentially a setter function for self._state
        if startTime is None:
            startTime = TIME_FUNC()

        if self._state == PLAYING:
            if self.isFinished():
                # if the animation doesn't loop and has already finished, then
                # calling play() causes it to replay from the beginning.
                self._playingStartTime = startTime
        elif self._state == STOPPED:
            # if animation was stopped, start playing from the beginning
            self._playingStartTime = startTime
        elif self._state == PAUSED:
            # if animation was paused, start playing from where it was paused
            self._playingStartTime = startTime - (self._pausedStartTime - self._playingStartTime)
        else:
            assert False, '_state attribute contains an invalid value: %s' % (str(self._state)[:40])
        self._state = PLAYING

    def pause(self, startTime=None):
        # Stop having the animation progress, and keep it at the current frame.

        # pause() is essentially a setter function for self._state
        if startTime is None:
            startTime = TIME_FUNC()

        if self._state == PAUSED:
            return # do nothing
        elif self._state == PLAYING:
            self._pausedStartTime = startTime
        elif self._state == STOPPED:
            rightNow = TIME_FUNC()
            self._playingStartTime = rightNow
            self._pausedStartTime = rightNow
        else:
            assert False, '_state attribute contains an invalid value: %s' % (str(self._state)[:40])
        self._state = PAUSED

    def stop(self):
        # Reset the animation to the beginning frame, and do not continue playing

        # stop() is essentially a setter function for self._state
        assert self._state in (PLAYING, PAUSED, STOPPED), '_state attribute contains an invalid value: %s' % (str(self._state)[:40])
        if self._state == STOPPED:
            return # do nothing
        self._state = STOPPED

    def togglePause(self):
        # If paused, start playing. If playing, then pause.

        # togglePause() is essentially a setter function for self._state
        if self._state == PLAYING:
            self.pause()
        elif self._state in (PAUSED, STOPPED):
            self.play()
        else:
            assert False, '_state attribute contains an invalid value: %s' % (str(self._state)[:40])

    def framesAreSameSize(self):
        # Returns True if all the Surface objects in this animation object
        # have the same width and height. Otherwise, returns False
        width, height = self.getFrame(0).get_size()
        for i in range(len(self._images)):
            if self.getFrame(i).get_size() != (width, height):
                return False
        return True

    def getMaxSize(self):
        # Goes through all the Surface objects in this animation object
        # and returns the max width and max height that it finds. (These
        # widths and heights may be on different Surface objects.)
        frame_widths = []
        frame_heights = []
        for i in range(len(self._images)):
            frame_width, frame_height = self._images[i].get_size()
            frame_widths.append(frame_width)
            frame_heights.append(frame_height)
        max_width = max(frame_widths)
        max_height = max(frame_heights)

        return max_width, max_height

    def getRect(self):
        # Returns a pygame.Rect object for this animation object.
        # The top and left will be set to 0, 0, and the width and height
        # will be set to what is returned by getMaxSize().
        max_width, max_height = self.getMaxSize()
        return pygame.Rect(0, 0, max_width, max_height)

    def nextFrame(self, jump=1):
        # Set the elapsed time to the beginning of the next frame.
        # You can jump ahead by multiple frames by specifying a different
        # argument for jump.
        # Negative values have the same effect as calling prevFrame()
        self.currentFrameNum += int(jump)

    def prevFrame(self, jump=1):
        # Set the elapsed time to the beginning of the previous frame.
        # You can jump ahead by multiple frames by specifying a different
        # argument for jump.
        # Negative values have the same effect as calling nextFrame()
        self.currentFrameNum -= int(jump)

    def rewind(self, milliseconds=None):
        # Set the elapsed time back relative to the current elapsed time.
        if milliseconds is None:
            self.elapsed = 0.0
        else:
            self.elapsed -= milliseconds

    def fastForward(self, milliseconds):
        # Set the elapsed time forward relative to the current elapsed time.
        if milliseconds is None:
            self.elapsed = self._startTimes[-1]
        else:
            self.elapsed += milliseconds

    def _makeTransformedSurfacesIfNeeded(self):
        # Internal-method. Creates the Surface objects for the _transformedImages list.
        # Don't call this method.
        if self._transformedImages == []:
            self._transformedImages = [surf.copy() for surf in self._images]

    # Transformation methods.
    # (These are analogous to the pygame.transform.* functions, except they
    # are applied to all frames of the animation object.
    def flip(self, xbool, ybool):
        # Flips the image horizontally, vertically, or both.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.flip
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.flip(self.getFrame(i), xbool, ybool)

    def scale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Increases or decreases the size of the images.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale(self.getFrame(i), width_height)

    def rotate(self, angle):
        # Rotates the image.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotate
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotate(self.getFrame(i), angle)

    def rotozoom(self, angle, scale):
        # Rotates and scales the image simultaneously.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotozoom
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotozoom(self.getFrame(i), angle, scale)

    def scale2x(self):
        # NOTE: Does not support the DestSurface parameter
        # Double the size of the image using an efficient algorithm.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale2x
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale2x(self.getFrame(i))

    def smoothscale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Scales the image smoothly. (Computationally more expensive and
        # slower but produces a better scaled image.)
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.smoothscale
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.smoothscale(self.getFrame(i), width_height)

    # pygame.Surface method wrappers
    # These wrappers call their analogous pygame.Surface methods on all Surface objects in this animation.
    # They are here for the convenience of the module user. These calls will apply to the transform images,
    # and can have their effects undone by called clearTransforms()
    #
    # It is not advisable to call these methods on the individual Surface objects in self._images.
    def _surfaceMethodWrapper(self, wrappedMethodName, *args, **kwargs):
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            methodToCall = getattr(self._transformedImages[i], wrappedMethodName)
            methodToCall(*args, **kwargs)

    # There's probably a more terse way to generate the following methods,
    # but I don't want to make the code even more unreadable.
    def convert(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert
        self._surfaceMethodWrapper('convert', *args, **kwargs)

    def convert_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert_alpha
        self._surfaceMethodWrapper('convert_alpha', *args, **kwargs)

    def set_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_alpha
        self._surfaceMethodWrapper('set_alpha', *args, **kwargs)

    def scroll(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.scroll
        self._surfaceMethodWrapper('scroll', *args, **kwargs)

    def set_clip(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_clip
        self._surfaceMethodWrapper('set_clip', *args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_colorkey
        self._surfaceMethodWrapper('set_colorkey', *args, **kwargs)

    def lock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.unlock
        self._surfaceMethodWrapper('lock', *args, **kwargs)

    def unlock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.lock
        self._surfaceMethodWrapper('unlock', *args, **kwargs)

    # Getter and setter methods for properties
    def _propGetRate(self):
        return self._rate

    def _propSetRate(self, rate):
        rate = float(rate)
        if rate < 0:
            raise ValueError('rate must be greater than 0.')
        self._rate = rate

    rate = property(_propGetRate, _propSetRate)

    def _propGetLoop(self):
        return self._loop

    def _propSetLoop(self, loop):
        if self.state == PLAYING and self._loop and not loop:
            # if we are turning off looping while the animation is playing,
            # we need to modify the _playingStartTime so that the rest of
            # the animation will play, and then stop. (Otherwise, the
            # animation will immediately stop playing if it has already looped.)
            self._playingStartTime = TIME_FUNC() - self.elapsed
        self._loop = bool(loop)

    loop = property(_propGetLoop, _propSetLoop)

    def _propGetState(self):
        if self.isFinished():
            self._state = STOPPED # if finished playing, then set state to STOPPED.

        return self._state

    def _propSetState(self, state):
        if state not in (PLAYING, PAUSED, STOPPED):
            raise ValueError('state must be one of pyganim.PLAYING, pyganim.PAUSED, or pyganim.STOPPED')
        if state == PLAYING:
            self.play()
        elif state == PAUSED:
            self.pause()
        elif state == STOPPED:
            self.stop()

    state = property(_propGetState, _propSetState)

    def _propGetVisibility(self):
        return self._visibility

    def _propSetVisibility(self, visibility):
        self._visibility = bool(visibility)

    visibility = property(_propGetVisibility, _propSetVisibility)

    def _propSetElapsed(self, elapsed):
        # Set the elapsed time to a specific value.
        # NOTE: elapsed is in milliseconds

        if self.state == STOPPED:
            self.state = PAUSED

        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getBoundedValue(0, elapsed, self._startTimes[-1])

        rightNow = TIME_FUNC()
        self._playingStartTime = rightNow - (elapsed * self.rate)

        if self.state in (PAUSED, STOPPED):
            self.state = PAUSED # if stopped, then set to paused
            self._pausedStartTime = rightNow

    def _propGetElapsed(self):
        # To prevent infinite recursion, don't use the self.state property,
        # just read/set self._state directly because the state getter calls
        # this method.

        # NOTE: Elapsed is in milliseconds, not seconds.
        assert self._state in (PLAYING, PAUSED, STOPPED), '_state attribute contains an invalid value: %s' % (str(self._state)[:40])

        # Find out how long ago the play()/pause() functions were called.
        if self._state == STOPPED:
            # if stopped, then just return 0
            return 0
        elif self._state == PLAYING:
            # if playing, then draw the current frame (based on when the animation
            # started playing). If not looping and the animation has gone through
            # all the frames already, then draw the last frame.
            elapsed = (TIME_FUNC() - self._playingStartTime) * self.rate
        elif self._state == PAUSED:
            # if paused, then draw the frame that was playing at the time the
            # PygAnimation object was paused
            elapsed = (self._pausedStartTime - self._playingStartTime) * self.rate

        elapsed = int(elapsed)

        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getBoundedValue(0, elapsed, self._startTimes[-1])
        return int(elapsed)

    elapsed = property(_propGetElapsed, _propSetElapsed)

    def _propGetCurrentFrameNum(self):
        # Return the frame number of the frame that will be currently
        # displayed if the animation object were drawn right now.
        return findStartTime(self._startTimes, self.elapsed)

    def _propSetCurrentFrameNum(self, frameNum):
        # Change the elapsed time to the beginning of a specific frame.
        if self._state == STOPPED:
            self._state = PAUSED # setting the frame num automatically puts it as paused.

        if self.loop:
            frameNum = frameNum % len(self._images)
        else:
            frameNum = getBoundedValue(0, frameNum, len(self._images)-1)
        self.elapsed = self._startTimes[frameNum]

    currentFrameNum = property(_propGetCurrentFrameNum, _propSetCurrentFrameNum)


def getBoundedValue(lowerBound, value, upperBound):
    # Returns the value within the bounds of the lower and upper bound parameters.
    # If value is less than lowerBound, then return lowerBound.
    # If value is greater than upperBound, then return upperBound.
    # Otherwise, just return value as it is.
    if upperBound < lowerBound:
        upperBound, lowerBound = lowerBound, upperBound

    if value < lowerBound:
        return lowerBound
    elif value > upperBound:
        return upperBound
    return value


def findStartTime(startTimes, target):
    # With startTimes as a list of sequential numbers and target as a number,
    # returns the index of the number in startTimes that preceeds target.
    #
    # For example, if startTimes was [0, 2000, 4500, 7300, 10000] and target was 6000,
    # then findStartTime() would return 2. If target was 12000, returns 4.
    assert startTimes[0] == 0, 'The first value in the start times list should always be 0.'
    lb = 0 # "lb" is lower bound
    ub = len(startTimes) - 1 # "ub" is upper bound

    # handle special cases:
    if len(startTimes) == 0:
        return 0
    if target >= startTimes[-1]:
        return ub - 1

    # perform binary search:
    while True:
        i = int((ub - lb) / 2) + lb

        if startTimes[i] == target or (startTimes[i] < target and startTimes[i+1] > target):
            if i == len(startTimes):
                return i - 1
            else:
                return i

        if startTimes[i] < target:
            lb = i
        elif startTimes[i] > target:
            ub = i


def audioPlayback(sounds):
    for i in sounds:
        i.set_volume(VOLUME)
    random.choice(sounds).play()


class Options(GameState):
    def __init__(self, name, button_dict):
        super(Options, self).__init__()
        self.name = name
        self.button_dict = button_dict

    def update(self):
        for button in self.button_dict:
            button.get_event()

    def draw(self, surface):
        for button in self.button_dict:
            button.draw(surface)


class OptionsHandler(Options):
    def __init__(self):
        super(OptionsHandler, self).__init__('null', {})
        self.options_dict = {'options': Options('base', {Button((0, 0), 'Sound Settings', 'sounds', type=('enter', 'sounds')),
                                                      Button((0, 100), 'Done', 'exit', type=('exit'))
                                                      }),
                             'sounds': Options('sounds', {Button((0, 0), 'Master Volume', 'master_volume', type=('slider', 0, 100)),
                                                          Button((0, 100), 'Sound Effects', 'effects_volume', type=('slider', 0, 100)),
                                                          Button((0, 200), 'Music', 'music_volume', type=('slider', 0, 100)),
                                                          Button((0, 300), 'Done', 'back_sounds', type=('exit'))
                                                          })
                             }
        self.reset()

        self.background = pygame.image.load(os.path.join("resources/images/gui", "options_background.png")).convert()

    def update(self):
        if self.stack:
            if self.stack[-1]:
                self.stack[-1].update()

    def reset(self):
        self.stack = []
        self.done = False

    def create_state(self, state):
        """ Create a state to the dictionary for later """
        self.options_dict[state.name] = state

    def push_state(self, name):
        """ Push a state to the top of the stack by name """
        if not name in self.options_dict:
            return
        self.stack.append(self.options_dict[name])

    def pull_state(self):
        """ Remove the current top-level state from the stack """
        self.stack.pop(-1)
        if not self.stack:
            game.state.options_open = False

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        self.stack[-1].draw(surface)


class Button(object):
    def __init__(self, pos, text, name, type=None):
        self.type = None
        self.pos = pos
        self.text = text
        self.font = pygame.font.Font(os.path.join("resources/font", "boxy_bold.ttf"), 16)
        self.title = self.font.render(self.text, True, pygame.Color("white"))
        self.sound = [pygame.mixer.Sound(os.path.join("resources/sounds/ui", "button_press.wav"))]
        self.inactive = pygame.image.load(os.path.join("resources/images/gui", "button_inactive.png")).convert()
        self.active = pygame.image.load(os.path.join("resources/images/gui", "button_active.png")).convert()
        self.name = name
        self.type = None
        self.call_directory_name = None
        self.range = None
        self.hover = False

        if type:
            if isinstance(type, tuple):
                self.type = type[0]
            else:
                self.type = type
            if self.type is 'enter':
                self.call_directory_name = type[1]
            if self.type is 'exit':
                pass
            if self.type is 'toggle':
                pass
            if self.type is 'slider':
                self.range = type[1:]

        self._image = pygame.Surface((256, 32))
        self.image = None
        self.rect = self._image.get_rect()
        self.title_rect = self.title.get_rect(center=(int(self.rect.w/2), int(self.rect.h/2)))


    def get_event(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if self.pos[0] < mouse[0] < self.pos[0] + self.rect.w and self.pos[1] < mouse[1] < self.pos[1] + self.rect.h:
            self.hover = True
            if click[0] is 1:
                audioPlayback(self.sound)
                if self.type is 'enter':
                    if self.call_directory_name:
                        options.push_state(self.call_directory_name)
                        game.state.options_open = True
                if self.type is 'exit':
                    if len(options.stack) > 0:
                        options.pull_state()
                if self.type is 'play':
                    game.state.music.fadeout(2000)
                    game.state.next_state = "GAMEPLAY"
                    game.cutscene.start(fadeout=200, fadein=200, fadeout_start=200, fadein_start=500, name='switch_play')
                if self.type is 'menu':
                    game.state.next_state = "MENU"
                    game.cutscene.start(fadeout=100, fadein=100, fadeout_start=0, fadein_start=200, name='switch_menu')
                if self.type is 'quit':
                    game.state.quit = True
        else:
            self.hover = False

    def draw(self, surface):
        if self.hover:
            surface.blit(self.active, self.pos)
        else:
            surface.blit(self.inactive, self.pos)
        surface.blit(self.title, tuple(map(sum, zip(self.title_rect, self.pos))))


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE.size, HWSURFACE | DOUBLEBUF | RESIZABLE)
    options = OptionsHandler()
    states = {"MENU": Menu(),
                "GAMEPLAY": GamePlay()}
    game = Game(screen, states, "MENU")
    game.run()
    pygame.quit()
    sys.exit()