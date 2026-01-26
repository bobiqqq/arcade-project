import arcade
import os
from bullet import Bullet
from constants import *
from hero import Hero
from enemy import Enemy
import random
from pyglet.graphics import Batch


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.batch = None
        self.start_text = None
        self.any_key_text = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.batch = None
        self.start_text = None
        self.any_key_text = None

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Dungeon Runner",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "SPACE — start   ESC — quit",
            self.window.width / 2,
            self.window.height / 2 - 10,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()
            return
        if key == arcade.key.SPACE:
            game_view = DungeonRunner()
            game_view.setup()
            self.window.show_view(game_view)


class BeetwenLevel(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.batch = None
        self.start_text = None
        self.any_key_text = None
        self.level = level
        # self.level.player.has_key = False

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.batch = None
        self.start_text = None
        self.any_key_text = None

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Выберите улучшение",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "1,2,3 - выбор      ENTER - далее",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "1: Увеличить здоровье на 20",
            self.window.width / 2,
            self.window.height / 2 - 50,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "2: Увеличить урон на 3",
            self.window.width / 2,
            self.window.height / 2 - 80,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "3: Увеличить скорость на 7%",
            self.window.width / 2,
            self.window.height / 2 - 110,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.level.player.hp += 20
            self.window.show_view(self.level)
        elif key == arcade.key.KEY_2:
            self.level.player.damage += 3
            self.window.show_view(self.level)
        elif key == arcade.key.KEY_3:
            self.level.player.speed *= 1.07
            self.level.player.speed = round(self.level.player.speed)
            self.window.show_view(self.level)
        elif key == arcade.key.ENTER:
            self.window.show_view(self.level)

class GameOver(arcade.View):
    def __init__(self, player):
        super().__init__()
        self.batch = None
        self.start_text = None
        self.any_key_text = None
        self.player = player

        self.levels = self.player.stats["levels"]
        self.coins = self.player.stats["coins"]
        self.kills = self.player.stats["kills"]
        
        self.score =  self.levels * 100
        self.score += self.coins * 10
        self.score += self.kills * 50

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.batch = None
        self.start_text = None
        self.any_key_text = None

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Игра закончена",
            self.window.width / 2,
            self.window.height / 2 + 60,
            arcade.color.WHITE,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Счет: {self.score}",
            self.window.width / 2,
            self.window.height / 2 - 15,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Убийства: {self.kills}",
            self.window.width / 2,
            self.window.height / 2 - 40,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Уровней пройдено: {self.levels}",
            self.window.width / 2,
            self.window.height / 2 - 65,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Монет собрано: {self.coins}",
            self.window.width / 2,
            self.window.height / 2 - 90,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
        )


class DungeonRunner(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)
        self.world_camera = arcade.camera.Camera2D()
        self.world_camera.zoom = 0.7 * (SCREEN_HEIGHT // 600)
        self.gui_camera = arcade.camera.Camera2D() 

    def setup(self, level_path="levels/level_01.tmx", hero=None):
        base_dir = os.path.dirname(__file__)
        if not os.path.isabs(level_path):
            level_path = os.path.join(base_dir, level_path)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.key_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.level_list = ["levels/level_01.tmx", "levels/level_02.tmx"]

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
                    self.player = Hero() if hero is None else hero
                    self.player.center_x = x
                    self.player.center_y = y
                    self.player_list.append(self.player)
                elif obj.name == "enemy":
                    enemy = Enemy(x, y)
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

        if self.player is not None and self.player.stats["levels"] != 0:
            for enemy in self.enemy_list:
                buff = 1 + (self.player.stats["levels"] / 10)
                enemy.hp *= buff
                enemy.damage *= buff

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
        self.gui_camera.use()
        arcade.draw_text(
            f"HP: {self.player.hp} | Coins: {self.player.coins} | {self.player.damaged_end} | {self.player.damage} | {self.player.speed}",
            10, self.window.height - 30,
            arcade.color.WHITE, 18
        )

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
        self.check_damage()

        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            CAMERA_LERP,
        )

        if self.player.damaged_end > 0:
            self.player.damaged_end -= delta_time

    def check_pickups(self):
        for coin in arcade.check_for_collision_with_list(self.player, self.coin_list):
            coin.remove_from_sprite_lists()
            self.player.coins += 1
            self.player.stats["coins"] += 1

        for key in arcade.check_for_collision_with_list(self.player, self.key_list):
            key.remove_from_sprite_lists()
            self.player.has_key = True

    def check_damage(self):
        for enemy in arcade.check_for_collision_with_list(self.player, self.enemy_list):
            self.player.get_damage(enemy.damage)
            if self.player.hp <= 0:
                self.game_over()
        for bomb in arcade.check_for_collision_with_list(self.player, self.bomb_list):
            self.player.get_damage(25)
            if self.player.hp <= 0:
                self.game_over()
            bomb.remove_from_sprite_lists()
            break

    def game_over(self):
        self.window.show_view(GameOver(self.player))

    def check_exit(self):
        if not self.player.has_key:
            return
        if arcade.check_for_collision_with_list(self.player, self.exit_list):
            self.player.stats["levels"] += 1
            new_level = DungeonRunner()
            new_level.setup(level_path=random.choice(self.level_list), hero=self.player)
            self.window.show_view(BeetwenLevel(new_level))
            return  

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
            self.player.stats["kills"] += 1

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
                damage=self.player.damage,
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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "DungeonRunner")
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()