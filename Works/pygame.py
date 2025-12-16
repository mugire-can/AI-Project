"""Minimal pygame stub for import-time compatibility in CI/testing environments.
This stub does not implement full functionality; it's only intended to allow
modules that `import pygame` at top-level to be imported when real pygame
is not installed.
"""
from collections import defaultdict

# Basic constants used across the project
K_a = 97
K_d = 100
K_w = 119
K_s = 115
K_LEFT = 276
K_RIGHT = 275
K_UP = 273
K_DOWN = 274
K_SPACE = 32
K_TAB = 9
K_q = 113
K_e = 101
K_1 = 49
K_2 = 50
K_3 = 51
K_4 = 52
K_KP_8 = 264
K_KP_5 = 261
K_KP_0 = 256
K_KP_PERIOD = 267
K_SEMICOLON = 59
K_F = 102
K_H = 104
K_T = 116
K_R = 114
K_Y = 121
K_G = 103
K_X = 120
K_ESCAPE = 27
K_RETURN = 13

SRCALPHA = 1

_screen = None

def init():
    return None

class mixer:
    @staticmethod
    def init():
        return None

    class Sound:
        def __init__(self, path):
            self.path = path
        def play(self):
            return None

class display:
    @staticmethod
    def set_mode(size):
        return Surface(size)
    @staticmethod
    def set_caption(caption):
        return None

class time:
    @staticmethod
    def get_ticks():
        return 0

class font:
    class Font:
        def __init__(self, name, size):
            self.name = name
            self.size = size
        def render(self, text, antialias, color):
            surf = Surface((len(text) * (self.size // 2 + 1) + 2, self.size + 2))
            return surf

class transform:
    @staticmethod
    def smoothscale(surf, size):
        return Surface(size)

    @staticmethod
    def rotate(surf, angle):
        return surf

# Minimal draw module used by game code
class draw:
    @staticmethod
    def line(surface, color, start_pos, end_pos, width=1):
        return None
    @staticmethod
    def circle(surface, color, center, radius, width=0):
        return None
    @staticmethod
    def ellipse(surface, color, rect, width=0):
        return None
    @staticmethod
    def rect(surface, color, rect, width=0):
        return None
    @staticmethod
    def polygon(surface, color, points, width=0):
        return None

class Surface:
    def __init__(self, size=(1,1), flags=0):
        self._w = int(size[0])
        self._h = int(size[1])
    def fill(self, color):
        return None
    def blit(self, src, dest):
        return None
    def get_width(self):
        return self._w
    def get_height(self):
        return self._h
    def get_rect(self, **kwargs):
        return Rect(0,0,self._w,self._h)
    def convert_alpha(self):
        return self

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x; self.y = y; self.w = w; self.h = h
    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)
    def collidepoint(self, pos):
        x,y = pos
        return self.x <= x <= self.x+self.w and self.y <= y <= self.y+self.h

class event:
    QUIT = 256
    KEYDOWN = 768

class key:
    @staticmethod
    def get_pressed():
        # Return a mapping that returns False for any key
        return defaultdict(lambda: False)

def image_load(path):
    return Surface((10,10))

# Provide pygame.image namespace
class image:
    @staticmethod
    def load(path):
        return image_load(path)

# Provide attributes that some code may import from pygame directly
Surface = Surface
Rect = Rect
Font = font.Font

# Expose a minimal namespace for pygame.colorkeys if needed

print_flag = False

# No-op for any other attributes

def __getattr__(name):
    # Provide fallbacks for attributes not defined
    globals()[name] = lambda *a, **k: None
    return globals()[name]
