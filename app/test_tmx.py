import arcade
import os
from bullet import Bullet
from constants import *
from hero import Hero
import random

class DungeonRunner(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.world_camera.zoom = 0.7
        self.gui_camera = arcade.camera.Camera2D()

    def setup(self, level_path="levels/level_01.tmx"):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.level_list = [f"levels/level_01.tmx"]

        self.tile_map = arcade.load_tilemap(level_path, scaling=TILE_SCALING)

        self.floor_list = self.tile_map.sprite_lists["floor"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.collision_list = self.tile_map.sprite_lists["collision"]
        self.exit_list = self.tile_map.sprite_lists["exit"]

        self.shoot_sound = arcade.load_sound(":resources:/sounds/laser1.wav")
        self.keys_pressed = set()

        object_layer = self.tile_map.object_lists["Object Layer 1"]
        if object_layer:
            for obj in object_layer:
                x, y = obj.shape[0], obj.shape[1]
                if obj.name == "player_spawn":
                    self.player = Hero()
                    self.player.center_x = x
                    self.player.center_y = y
                    self.player.has_key = False
                    self.player.coins = 0
                    self.player_list.append(self.player)
                elif obj.name == "enemy":
                    enemy = arcade.Sprite(":resources:images/enemies/slimeBlue.png", scale=0.7)
                    enemy.center_x = x
                    enemy.center_y = y
                    enemy.hp = 30
                    self.enemy_list.append(enemy)
                elif obj.name == "coin":
                    coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.5)
                    coin.center_x = x
                    coin.center_y = y
                    self.coin_list.append(coin)
                elif obj.name == "key":
                    key = arcade.Sprite(":resources:images/items/keyYellow.png", scale=0.6)
                    key.center_x = x
                    key.center_y = y
                    self.key_list.append(key)
                elif obj.name == "bomb":
                    bomb = arcade.Sprite(":resources:images/tiles/bomb.png", scale=0.5)
                    bomb.center_x = x
                    bomb.center_y = y
                    self.bomb_list.append(bomb)

        if self.player and self.collision_list:
            self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.collision_list)

        self.world_camera.position = (self.player.center_x, self.player.center_y)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.floor_list.draw()
        self.wall_list.draw()
        self.enemy_list.draw()
        self.coin_list.draw()
        self.key_list.draw()
        self.bomb_list.draw()
        self.player_list.draw()
        self.exit_list.draw()
        self.bullet_list.draw()

    def on_update(self, delta_time):
        if self.physics_engine:
            self.physics_engine.update()
        self.player.update(delta_time, self.keys_pressed)

        position = self.player.center_x, self.player.center_y
        self.player_list.update_animation()
        self.bullet_list.update(delta_time)
        self.check_pickups()
        self.check_exit()
        self.check_bullets_hit_enemies()

        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP,
        )

    def check_pickups(self):
        for coin in arcade.check_for_collision_with_list(self.player, self.coin_list):
            coin.remove_from_sprite_lists()
            self.player.coins += 1

        for key in arcade.check_for_collision_with_list(self.player, self.key_list):
            key.remove_from_sprite_lists()
            self.player.has_key = True

    def check_exit(self):
        if not self.player.has_key:
            return
        if arcade.check_for_collision_with_list(self.player, self.exit_list):
            level = random.choice(self.level_list)
            self.setup(level_path=level)

    def check_bullets_hit_enemies(self):
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if not hit_list:
                hit_walls = arcade.check_for_collision_with_list(bullet, self.wall_list)
                if not hit_walls:
                    continue
                else:
                    bullet.remove_from_sprite_lists()

            bullet.remove_from_sprite_lists()
            for enemy in hit_list:
                self.damage_enemy(enemy, bullet.damage)

    def damage_enemy(self, enemy, damage):
        enemy.hp -= damage
        if enemy.hp <= 0:
            enemy.remove_from_sprite_lists()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_pos = self.world_camera.unproject((x, y))
            target_x, target_y = world_pos[0], world_pos[1]
            bullet = Bullet(
                self.player.center_x,
                self.player.center_y,
                target_x,
                target_y,
                speed=BULLET_SPEED,
                damage=BULLET_DAMAGE,
                lifetime=BULLET_LIFETIME,
            )
            self.bullet_list.append(bullet)

            arcade.play_sound(self.shoot_sound)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


def main():
    window = DungeonRunner()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
