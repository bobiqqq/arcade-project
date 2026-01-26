from constants import *
import enum
import arcade


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()
        
        self.scale = 0.8
        self.speed = PLAYER_MOVEMENT_SPEED
        self.hp = 100
        self.damaged_end = 0
        self.damage = 10
        
        self.idle_texture = arcade.load_texture(":resources:/images/animated_characters/female_person/femalePerson_idle.png")
        self.texture = self.idle_texture
        
        self.walk_textures = []
        for i in range(0, 8):
            texture = arcade.load_texture(f":resources:/images/animated_characters/female_person/femalePerson_walk{i}.png")
            self.walk_textures.append(texture)
            
        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        
        self.is_walking = False
        self.face_direction = FaceDirection.RIGHT
        self.has_key = True
        self.coins = 0
        self.stats = {"kills": 0, "coins": 0, "levels": 0}
        self.if_damaged = False

    def update_animation(self, delta_time: float = 1/60):
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                if self.face_direction == FaceDirection.RIGHT:
                    self.texture = self.walk_textures[self.current_texture]
                else:
                    self.texture = self.walk_textures[self.current_texture].flip_horizontally()

        else:
            if self.face_direction == FaceDirection.RIGHT:
                self.texture = self.idle_texture
            else:
                self.texture = self.idle_texture.flip_horizontally()

       
    def update(self, delta_time, keys_pressed):
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy
        if dx < 0:
            self.face_direction = FaceDirection.LEFT
        elif dx > 0:
            self.face_direction = FaceDirection.RIGHT
        
        self.change_x = dx
        self.change_y = dy
        
        self.is_walking = dx or dy

    def get_damage(self, damage_value):
        if self.damaged_end > 0:
            return

        self.hp -= damage_value
        self.damaged_end = 1
        
                
