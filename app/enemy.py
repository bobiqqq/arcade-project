from constants import *
from bullet import Bullet
import math
import random
import arcade

class Enemy(arcade.Sprite):
    def __init__(self, x=None, y=None):
        super().__init__()
        # Основные характеристики
        self.hp = 50
        self.center_x = x
        self.center_y = y
        self.damage = 8
    
    def get_damage(self, damage):
        self.hp -= damage

class SlimeEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Характеристики класса слайма и подгрузка текстуры
        self.speed = 150
        self.aggro_radius = 400
        self.texture = arcade.load_texture(":resources:images/enemies/slimeBlue.png")

    # Интеллект врага: пытается изменить координаты в сторону игрока
    def update_ai(self, player, collision_list, delta_time, level=None):
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = (dx**2 + dy**2) ** 0.5
        if dist > self.aggro_radius:
            return
        step_x = (dx / dist) * self.speed * delta_time
        step_y = (dy / dist) * self.speed * delta_time

        old_x, old_y = self.center_x, self.center_y
        self.center_x += step_x
        self.center_y += step_y
        if arcade.check_for_collision_with_list(self, collision_list):
            self.center_x, self.center_y = old_x, old_y

    def get_damage(self, damage):
        super().get_damage(damage)

class ShooterEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Характеристики класса робота и подгрузка текстуры
        self.fire_cd = 1.2
        self.fire_timer = 1.2
        self.fire_radius = 400
        self.bullet_speed = 700
        self.texture = arcade.load_texture(":resources:images/animated_characters/robot/robot_idle.png")

    # Создает объект пули, направленный в сторону игрока
    def update_ai(self, player, collision_list, delta_time, level=None):
        if level is None:
            return
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = (dx**2 + dy**2) ** 0.5 
        if dist > self.fire_radius:
            return

        # Вычисление "перезарядки"
        self.fire_timer -= delta_time
        if self.fire_timer > 0:
            return
        self.fire_timer = self.fire_cd

        bullet = Bullet(self.center_x, self.center_y, player.center_x, player.center_y, speed=BULLET_SPEED, damage=self.damage)
        level.enemy_bullet_list.append(bullet)
    
    def get_damage(self, damage):
        super().get_damage(damage)
