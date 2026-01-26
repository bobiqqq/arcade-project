from constants import *

import arcade

class Enemy(arcade.Sprite):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.damage = 10
        self.hp = 50
        self.texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png")
        self.center_x = x
        self.center_y = y