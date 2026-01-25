import math

import arcade


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, speed=800, damage=10, lifetime=1.2):
        super().__init__()
        self.texture = arcade.load_texture(":resources:images/space_shooter/laserBlue01.png")
        self.center_x = start_x
        self.center_y = start_y
        self.damage = damage
        self.lifetime = lifetime
        self.time_alive = 0.0

        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        self.angle = math.degrees(-angle)

    def update(self, delta_time=1 / 60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        self.time_alive += delta_time
        if self.time_alive >= self.lifetime:
            self.remove_from_sprite_lists()

